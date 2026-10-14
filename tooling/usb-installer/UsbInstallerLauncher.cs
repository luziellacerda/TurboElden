using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;
using System.Web.Script.Serialization;

internal static class UsbInstallerLauncher
{
    private sealed class Manifest
    {
        public string revision { get; set; }
        public string warning { get; set; }
        public string apkPath { get; set; }
        public string sha256 { get; set; }
        public long bytes { get; set; }
    }

    private sealed class UsbDevice
    {
        public string Serial { get; set; }
        public string Model { get; set; }
        public string Alias { get; set; }
        public string UsbVerificationMethod { get; set; }

        public override string ToString()
        {
            return (String.IsNullOrWhiteSpace(Alias) ? "Telefone" : Alias) + " — " +
                   (String.IsNullOrWhiteSpace(Model) ? "Android" : Model) +
                   "  ·  USB …" + (String.IsNullOrEmpty(Serial) ? "????" :
                       Serial.Substring(Math.Max(0, Serial.Length - 4)));
        }
    }

    private sealed class UsbListing
    {
        public string revision { get; set; }
        public string warning { get; set; }
        public UsbDevice[] Authorized { get; set; }
        public int UnauthorizedCount { get; set; }
        public int OfflineCount { get; set; }
        public int ExcludedCount { get; set; }
    }

    private sealed class CommandResult
    {
        public int ExitCode;
        public string Output;
        public string Error;
    }

    private sealed class CommandRequest
    {
        public string Kind;
        public string Arguments;
        public bool StreamOutput;
    }

    private sealed class InstallReceipt
    {
        public string resultCode { get; set; }
        public bool installAttempted { get; set; }
        public bool installSuccess { get; set; }
        public string deviceModel { get; set; }
    }

    private sealed class DashboardProgressBar : Control
    {
        private readonly System.Windows.Forms.Timer animation = new System.Windows.Forms.Timer();
        private int value;
        private int sweep;
        private bool indeterminate;
        private Color accent = Color.FromArgb(64, 174, 255);

        public DashboardProgressBar()
        {
            DoubleBuffered = true;
            Height = 18;
            animation.Interval = 90;
            animation.Tick += delegate { sweep += 12; Invalidate(); };
        }

        public void ShowMeasured(int percentage, Color color)
        {
            animation.Stop();
            indeterminate = false;
            value = Math.Max(0, Math.Min(100, percentage));
            accent = color;
            Invalidate();
        }

        public void ShowWorking(Color color)
        {
            value = 0;
            accent = color;
            indeterminate = true;
            sweep = 0;
            animation.Start();
            Invalidate();
        }

        private static GraphicsPath Rounded(Rectangle rect, int radius)
        {
            var path = new GraphicsPath();
            int diameter = Math.Min(radius * 2, Math.Min(rect.Width, rect.Height));
            if (diameter <= 0) { path.AddRectangle(rect); return path; }
            path.AddArc(rect.Left, rect.Top, diameter, diameter, 180, 90);
            path.AddArc(rect.Right - diameter, rect.Top, diameter, diameter, 270, 90);
            path.AddArc(rect.Right - diameter, rect.Bottom - diameter, diameter, diameter, 0, 90);
            path.AddArc(rect.Left, rect.Bottom - diameter, diameter, diameter, 90, 90);
            path.CloseFigure();
            return path;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
            var track = new Rectangle(0, 1, Math.Max(1, Width - 1), Math.Max(1, Height - 2));
            using (var shape = Rounded(track, 8))
            using (var background = new SolidBrush(Color.FromArgb(37, 54, 77)))
            {
                e.Graphics.FillPath(background, shape);
                e.Graphics.SetClip(shape);
                if (indeterminate)
                {
                    int block = Math.Max(64, Width / 4);
                    int x = (sweep % (Width + block)) - block;
                    using (var brush = new LinearGradientBrush(
                        new Rectangle(x, 0, block, Height),
                        Color.FromArgb(65, accent), accent, LinearGradientMode.Horizontal))
                        e.Graphics.FillRectangle(brush, x, 0, block, Height);
                }
                else if (value > 0)
                {
                    var fill = new Rectangle(0, 1, Math.Max(1, Width * value / 100), Math.Max(1, Height - 2));
                    using (var brush = new LinearGradientBrush(fill, accent,
                        Color.FromArgb(Math.Min(255, accent.R + 32),
                                       Math.Min(255, accent.G + 32),
                                       Math.Min(255, accent.B + 32)), LinearGradientMode.Horizontal))
                        e.Graphics.FillRectangle(brush, fill);
                }
                e.Graphics.ResetClip();
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing) animation.Dispose();
            base.Dispose(disposing);
        }
    }

    private sealed class InstallerForm : Form
    {
        private static readonly Color Canvas = Color.FromArgb(11, 20, 34);
        private static readonly Color Surface = Color.FromArgb(22, 35, 53);
        private static readonly Color SurfaceRaised = Color.FromArgb(27, 44, 65);
        private static readonly Color Ink = Color.FromArgb(239, 246, 255);
        private static readonly Color Muted = Color.FromArgb(155, 177, 198);
        private static readonly Color Blue = Color.FromArgb(64, 174, 255);
        private static readonly Color Green = Color.FromArgb(104, 216, 174);
        private static readonly Color Amber = Color.FromArgb(245, 190, 101);
        private static readonly Color Red = Color.FromArgb(247, 122, 125);
        private readonly string folder;
        private readonly string script;
        private readonly string manifestFile;
        private readonly Panel header = new Panel();
        private readonly Panel deviceCard = new Panel();
        private readonly Panel confirmationCard = new Panel();
        private readonly Panel operationCard = new Panel();
        private readonly Panel actionRow = new Panel();
        private readonly Panel brandMark = new Panel();
        private readonly Label brandLetter = new Label();
        private readonly Label title = new Label();
        private readonly Label version = new Label();
        private readonly Label candidate = new Label();
        private readonly Label warning = new Label();
        private readonly Label devicesHeading = new Label();
        private readonly Label stage = new Label();
        private readonly Label status = new Label();
        private readonly Label statusDetail = new Label();
        private readonly Label progressCaption = new Label();
        private readonly Label actionHint = new Label();
        private readonly Label[] stepLabels = new Label[4];
        private readonly ListBox phones = new ListBox();
        private readonly CheckBox idleConfirmed = new CheckBox();
        private readonly Button refresh = new Button();
        private readonly Button install = new Button();
        private readonly Button verify = new Button();
        private readonly Button close = new Button();
        private readonly DashboardProgressBar progress = new DashboardProgressBar();
        private readonly TextBox log = new TextBox();
        private readonly LinkLabel receipts = new LinkLabel();
        private readonly LinkLabel details = new LinkLabel();
        private readonly List<string> knownSerials = new List<string>();
        private readonly Stopwatch elapsed = new Stopwatch();
        private readonly System.Windows.Forms.Timer elapsedTimer = new System.Windows.Forms.Timer();
        private bool manifestValid;
        private bool busy;
        private bool retryAvailable;
        private bool installOutcomeUncertain;
        private string uncertainSerial;
        private int completedStages;
        private int activeStage = -1;
        private int blockedStage = -1;
        private string captionBase = "";
        private string currentKind;

        public InstallerForm(string baseFolder, string scriptPath, string manifestPath)
        {
            folder = baseFolder;
            script = scriptPath;
            manifestFile = manifestPath;
            Text = "TurboStations — instalação por USB";
            Font = new Font("Segoe UI", 9.5F);
            AutoScaleMode = AutoScaleMode.Dpi;
            BackColor = Canvas;
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.Sizable;
            MinimumSize = new Size(840, 700);
            ClientSize = new Size(900, 660);

            header.BackColor = Color.FromArgb(15, 31, 51);
            brandMark.BackColor = Blue;
            brandLetter.Text = "T";
            brandLetter.Font = new Font("Segoe UI", 17F, FontStyle.Bold);
            brandLetter.ForeColor = Canvas;
            brandLetter.TextAlign = ContentAlignment.MiddleCenter;
            brandMark.Controls.Add(brandLetter);
            title.Text = "TurboStations";
            title.ForeColor = Ink;
            title.Font = new Font("Segoe UI Semibold", 20F, FontStyle.Bold);
            version.ForeColor = Blue;
            version.Font = new Font("Segoe UI Semibold", 8.5F, FontStyle.Bold);
            candidate.Text = "VERSÃO DE TESTE";
            candidate.TextAlign = ContentAlignment.MiddleCenter;
            candidate.BackColor = Color.FromArgb(70, 54, 38);
            candidate.ForeColor = Amber;
            candidate.Font = new Font("Segoe UI Semibold", 8F, FontStyle.Bold);
            warning.ForeColor = Muted;
            warning.Font = new Font("Segoe UI", 8.7F);
            warning.AutoEllipsis = true;
            header.Controls.AddRange(new Control[] { brandMark, title, version, candidate, warning });

            deviceCard.BackColor = Surface;
            devicesHeading.Text = "01   TELEFONE CONECTADO";
            devicesHeading.ForeColor = Muted;
            devicesHeading.Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold);
            refresh.Text = "ATUALIZAR USB";
            StyleSecondaryButton(refresh);
            refresh.Click += delegate { StartRefresh(); };
            phones.BackColor = SurfaceRaised;
            phones.ForeColor = Ink;
            phones.BorderStyle = BorderStyle.None;
            phones.DrawMode = DrawMode.OwnerDrawFixed;
            phones.ItemHeight = 43;
            phones.DrawItem += DrawPhone;
            phones.IntegralHeight = false;
            phones.SelectionMode = SelectionMode.One;
            phones.SelectedIndexChanged += delegate {
                retryAvailable = false;
                idleConfirmed.Checked = false;
                var selected = phones.SelectedItem as UsbDevice;
                installOutcomeUncertain = selected != null &&
                    String.Equals(selected.Serial, uncertainSerial, StringComparison.Ordinal);
                if (installOutcomeUncertain && !busy)
                    ShowBlocked(2, 2, "Resultado anterior incerto",
                        "Confira no telefone se a atualização terminou.",
                        "Feche e reabra o instalador após conferir este aparelho.", Red);
                UpdateButtons();
            };
            deviceCard.Controls.AddRange(new Control[] { devicesHeading, refresh, phones });

            confirmationCard.BackColor = Surface;
            idleConfirmed.Text = "Saí da partida, concluí downloads e deixei o TurboStations ou o Android na tela inicial.";
            idleConfirmed.ForeColor = Ink;
            idleConfirmed.BackColor = Surface;
            idleConfirmed.Font = new Font("Segoe UI", 9.5F);
            idleConfirmed.CheckedChanged += delegate { UpdateButtons(); };
            confirmationCard.Controls.Add(idleConfirmed);

            operationCard.BackColor = Surface;
            stage.ForeColor = Blue;
            stage.Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold);
            status.ForeColor = Ink;
            status.Font = new Font("Segoe UI Semibold", 18F, FontStyle.Bold);
            status.AutoEllipsis = true;
            statusDetail.ForeColor = Muted;
            statusDetail.Font = new Font("Segoe UI", 9.5F);
            statusDetail.AutoEllipsis = true;
            progressCaption.ForeColor = Muted;
            progressCaption.Font = new Font("Segoe UI Semibold", 8.5F, FontStyle.Bold);
            actionHint.ForeColor = Muted;
            actionHint.BackColor = SurfaceRaised;
            actionHint.Font = new Font("Segoe UI", 9F);
            actionHint.TextAlign = ContentAlignment.MiddleLeft;
            operationCard.Controls.AddRange(new Control[] {
                stage, status, statusDetail, progressCaption, progress, actionHint
            });
            for (int i = 0; i < stepLabels.Length; i++)
            {
                stepLabels[i] = new Label();
                stepLabels[i].TextAlign = ContentAlignment.MiddleCenter;
                stepLabels[i].Font = new Font("Segoe UI Semibold", 8.5F, FontStyle.Bold);
                operationCard.Controls.Add(stepLabels[i]);
            }

            install.Text = "INSTALAR NO TELEFONE";
            StylePrimaryButton(install);
            install.Click += delegate { StartInstall(); };
            verify.Text = "VERIFICAR APK";
            StyleSecondaryButton(verify);
            verify.Click += delegate { StartValidation(); };
            close.Text = "FECHAR";
            StyleSecondaryButton(close);
            close.Click += delegate { Close(); };
            actionRow.Controls.AddRange(new Control[] { install, verify, close });

            log.Multiline = true;
            log.ReadOnly = true;
            log.ScrollBars = ScrollBars.Vertical;
            log.BackColor = Surface;
            log.ForeColor = Ink;
            details.Text = "DETALHES TÉCNICOS";
            details.LinkColor = Blue;
            details.ActiveLinkColor = Ink;
            details.VisitedLinkColor = Blue;
            details.LinkClicked += delegate { OpenDetails(); };
            receipts.Text = "ABRIR RECIBOS";
            receipts.LinkColor = Blue;
            receipts.ActiveLinkColor = Ink;
            receipts.VisitedLinkColor = Blue;
            receipts.LinkClicked += delegate { OpenReceipts(); };
            Controls.AddRange(new Control[] {
                header, deviceCard, confirmationCard, operationCard, actionRow, details, receipts
            });
            Resize += delegate { LayoutDashboard(); };
            elapsedTimer.Interval = 1000;
            elapsedTimer.Tick += delegate { UpdateElapsed(); };
            FormClosing += OnFormClosing;
            FormClosed += delegate { elapsedTimer.Dispose(); };
            Shown += delegate { BeginInvoke(new Action(StartRefresh)); };
            LayoutDashboard();
            ShowIdle("Aguardando telefone", "Conecte um aparelho por USB e autorize a depuração.");
            LoadManifest();
            UpdateButtons();
        }

        private static void StyleSecondaryButton(Button button)
        {
            button.FlatStyle = FlatStyle.Flat;
            button.FlatAppearance.BorderSize = 1;
            button.FlatAppearance.BorderColor = Color.FromArgb(69, 92, 116);
            button.BackColor = SurfaceRaised;
            button.ForeColor = Ink;
            button.Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold);
            button.Cursor = Cursors.Hand;
            button.UseVisualStyleBackColor = false;
        }

        private static void StylePrimaryButton(Button button)
        {
            button.FlatStyle = FlatStyle.Flat;
            button.FlatAppearance.BorderSize = 0;
            button.BackColor = Blue;
            button.ForeColor = Canvas;
            button.Font = new Font("Segoe UI Semibold", 10F, FontStyle.Bold);
            button.Cursor = Cursors.Hand;
            button.UseVisualStyleBackColor = false;
        }

        private void LayoutDashboard()
        {
            int width = ClientSize.Width;
            int height = ClientSize.Height;
            header.SetBounds(0, 0, width, 102);
            brandMark.SetBounds(24, 17, 54, 54);
            brandLetter.Dock = DockStyle.Fill;
            title.SetBounds(94, 12, Math.Max(200, width - 300), 40);
            version.SetBounds(96, 57, Math.Max(200, width - 300), 19);
            candidate.SetBounds(width - 177, 23, 153, 28);
            warning.SetBounds(24, 80, width - 48, 19);

            int cardWidth = width - 48;
            deviceCard.SetBounds(24, 114, cardWidth, 106);
            devicesHeading.SetBounds(20, 12, cardWidth - 205, 28);
            refresh.SetBounds(cardWidth - 170, 10, 150, 32);
            phones.SetBounds(20, 49, cardWidth - 40, 48);
            confirmationCard.SetBounds(24, 232, cardWidth, 50);
            idleConfirmed.SetBounds(18, 8, cardWidth - 36, 34);

            int operationBottom = height - 126;
            operationCard.SetBounds(24, 294, cardWidth, Math.Max(228, operationBottom - 294));
            stage.SetBounds(20, 17, cardWidth - 40, 20);
            status.SetBounds(20, 43, cardWidth - 40, 38);
            statusDetail.SetBounds(20, 82, cardWidth - 40, 24);
            progressCaption.SetBounds(20, 116, cardWidth - 40, 19);
            progress.SetBounds(20, 141, cardWidth - 40, 18);
            actionHint.SetBounds(20, 168, cardWidth - 40, 34);
            int chipsTop = operationCard.Height - 36;
            int gap = 7;
            int chipWidth = (cardWidth - 40 - gap * 3) / 4;
            for (int i = 0; i < stepLabels.Length; i++)
                stepLabels[i].SetBounds(20 + i * (chipWidth + gap), chipsTop, chipWidth, 23);

            actionRow.SetBounds(24, height - 114, cardWidth, 48);
            int primaryWidth = Math.Min(330, Math.Max(250, cardWidth / 2 - 35));
            install.SetBounds(0, 0, primaryWidth, 46);
            verify.SetBounds(primaryWidth + 12, 0, 160, 46);
            close.SetBounds(cardWidth - 126, 0, 126, 46);
            details.SetBounds(24, height - 47, 166, 21);
            receipts.SetBounds(208, height - 47, 140, 21);
        }

        private void DrawPhone(object sender, DrawItemEventArgs e)
        {
            if (e.Index < 0 || e.Index >= phones.Items.Count) return;
            var device = phones.Items[e.Index] as UsbDevice;
            if (device == null) return;
            bool selected = (e.State & DrawItemState.Selected) == DrawItemState.Selected;
            using (var background = new SolidBrush(selected ? Color.FromArgb(32, 72, 102) : SurfaceRaised))
                e.Graphics.FillRectangle(background, e.Bounds);
            if (selected)
                using (var accent = new SolidBrush(Blue))
                    e.Graphics.FillRectangle(accent, e.Bounds.Left, e.Bounds.Top, 4, e.Bounds.Height);
            string model = String.IsNullOrWhiteSpace(device.Model) ? "Telefone Android" : device.Model;
            string suffix = String.IsNullOrEmpty(device.Serial) ? "????" :
                device.Serial.Substring(Math.Max(0, device.Serial.Length - 4));
            using (var heading = new Font("Segoe UI Semibold", 10F, FontStyle.Bold))
            using (var meta = new Font("Segoe UI", 8.5F))
            using (var headingBrush = new SolidBrush(Ink))
            using (var metaBrush = new SolidBrush(Muted))
            {
                e.Graphics.DrawString(model, heading, headingBrush, e.Bounds.Left + 16, e.Bounds.Top + 3);
                e.Graphics.DrawString("USB autorizado  ·  aparelho …" + suffix,
                    meta, metaBrush, e.Bounds.Left + 17, e.Bounds.Top + 23);
            }
            if (selected) e.DrawFocusRectangle();
        }

        private void OpenDetails()
        {
            var window = new Form();
            window.Text = "TurboStations — detalhes técnicos";
            window.StartPosition = FormStartPosition.CenterParent;
            window.Size = new Size(800, 480);
            window.MinimumSize = new Size(600, 340);
            window.BackColor = Canvas;
            var copy = new TextBox();
            copy.Multiline = true;
            copy.ReadOnly = true;
            copy.ScrollBars = ScrollBars.Both;
            copy.WordWrap = false;
            copy.BackColor = Surface;
            copy.ForeColor = Ink;
            copy.Font = new Font("Consolas", 9F);
            copy.Dock = DockStyle.Fill;
            copy.Text = log.Text;
            window.Controls.Add(copy);
            window.Show(this);
        }

        private void UpdateElapsed()
        {
            if (busy && !String.IsNullOrEmpty(captionBase))
                progressCaption.Text = captionBase + "   ·   " + elapsed.Elapsed.ToString(@"mm\:ss");
        }

        private void SetActionHint(string message, Color color)
        {
            actionHint.Text = "   " + message;
            actionHint.ForeColor = color;
            actionHint.BackColor = Color.FromArgb(
                Math.Min(255, (SurfaceRaised.R * 4 + color.R) / 5),
                Math.Min(255, (SurfaceRaised.G * 4 + color.G) / 5),
                Math.Min(255, (SurfaceRaised.B * 4 + color.B) / 5));
        }

        private void UpdateStepLabels()
        {
            string[] names = { "1  CONFERIR APK", "2  PREPARAR USB", "3  INSTALAR", "4  VALIDAR" };
            for (int i = 0; i < stepLabels.Length; i++)
            {
                Label label = stepLabels[i];
                label.Text = names[i];
                bool complete = i < completedStages;
                bool active = i == activeStage;
                bool blocked = i == blockedStage;
                label.BackColor = blocked ? Color.FromArgb(74, 42, 52) :
                    complete ? Color.FromArgb(30, 72, 65) :
                    active ? Color.FromArgb(31, 72, 105) : SurfaceRaised;
                label.ForeColor = blocked ? Red : complete ? Green : active ? Blue : Muted;
            }
        }

        private void ShowIdle(string heading, string detail)
        {
            completedStages = 0;
            activeStage = -1;
            blockedStage = -1;
            stage.Text = "PRONTO PARA COMEÇAR";
            status.Text = heading;
            statusDetail.Text = detail;
            captionBase = "Progresso da instalação";
            progressCaption.Text = captionBase;
            progress.ShowMeasured(0, Blue);
            SetActionHint("Selecione o telefone e confirme que está livre.", Muted);
            UpdateStepLabels();
        }

        private void ShowStage(int index, int completed, string heading, string detail, bool working)
        {
            completedStages = completed;
            activeStage = index;
            blockedStage = -1;
            stage.Text = "ETAPA " + (index + 1) + " DE 4";
            status.Text = heading;
            statusDetail.Text = detail;
            captionBase = working ? (index == 0 ? "Conferindo o arquivo" : "Aguardando resposta do Android")
                : "Progresso medido";
            UpdateElapsed();
            if (working) progress.ShowWorking(Blue);
            else progress.ShowMeasured(completed * 25, Blue);
            SetActionHint("Mantenha o telefone conectado durante esta etapa.", Blue);
            UpdateStepLabels();
        }

        private void ShowBlocked(int index, int completed, string heading, string detail, string hint, Color color)
        {
            completedStages = completed;
            activeStage = -1;
            blockedStage = index;
            stage.Text = "INSTALAÇÃO INTERROMPIDA NA ETAPA " + (index + 1);
            status.Text = heading;
            statusDetail.Text = detail;
            captionBase = completed >= 3 ? "APK instalado; validação pendente" :
                completed >= 2 ? "Instalação iniciada; resultado não confirmado" :
                completed + " de 4 etapas concluídas; sem transferência";
            progressCaption.Text = captionBase;
            progress.ShowMeasured(completed * 25, color);
            SetActionHint(hint, color);
            UpdateStepLabels();
        }

        private void LoadManifest()
        {
            manifestValid = false;
            try
            {
                var manifest = new JavaScriptSerializer().Deserialize<Manifest>(
                    File.ReadAllText(manifestFile, Encoding.UTF8));
                if (manifest == null || String.IsNullOrWhiteSpace(manifest.revision))
                    throw new InvalidDataException("Manifesto sem revisão.");
                if (String.IsNullOrWhiteSpace(manifest.apkPath) ||
                    !Regex.IsMatch(manifest.sha256 ?? "", "^[a-fA-F0-9]{64}$") || manifest.bytes <= 0)
                    throw new InvalidDataException("Manifesto do APK incompleto.");
                string apk = Path.IsPathRooted(manifest.apkPath) ? manifest.apkPath :
                    Path.Combine(folder, manifest.apkPath);
                if (!File.Exists(apk) || new FileInfo(apk).Length != manifest.bytes)
                    throw new FileNotFoundException("APK ausente ou com tamanho diferente do manifesto.", apk);
                title.Text = "TurboStations";
                version.Text = "INSTALADOR USB   /   " + manifest.revision.ToUpperInvariant();
                warning.Text = "Pacote " + manifest.revision + " para teste  ·  confira o resultado no telefone antes de considerar estável.";
                if (!String.IsNullOrWhiteSpace(manifest.warning)) AppendLog(manifest.warning);
                manifestValid = true;
                if (!busy) ShowIdle("Pacote pronto", "Buscando telefones USB autorizados.");
            }
            catch (Exception error)
            {
                title.Text = "TurboStations";
                version.Text = "INSTALADOR USB   /   PACOTE INCOMPLETO";
                warning.Text = "O pacote de instalação está incompleto.";
                ShowBlocked(0, 0, "Pacote incompleto", "Confira o APK e o manifesto ao lado do instalador.",
                    "NENHUM APK FOI INSTALADO", Red);
                AppendLog("Instalação bloqueada: " + error.Message);
            }
        }

        private void OnFormClosing(object sender, FormClosingEventArgs e)
        {
            if (!busy) return;
            e.Cancel = true;
            MessageBox.Show(this, "Aguarde a operação terminar antes de fechar o instalador.",
                "Operação em andamento", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        private void SetStatus(string message)
        {
            status.Text = message;
        }

        private void OpenReceipts()
        {
            string path = Path.Combine(folder, "recibos-usb");
            if (!Directory.Exists(path)) return;
            try { Process.Start(new ProcessStartInfo { FileName = path, UseShellExecute = true }); }
            catch (Exception error) { AppendLog("Não foi possível abrir os recibos: " + error.Message); }
        }

        private bool HandleStage(string line)
        {
            const string marker = "TS_STAGE|";
            if (line == null || !line.StartsWith(marker, StringComparison.Ordinal)) return false;
            string code = line.Substring(marker.Length);
            if (currentKind == "validate")
            {
                if (code == "APK_VERIFIED")
                {
                    status.Text = "APK conferido";
                    statusDetail.Text = "Tamanho e SHA-256 correspondem ao pacote.";
                    progress.ShowMeasured(100, Green);
                    captionBase = "Leitura concluída";
                    UpdateElapsed();
                }
                return true;
            }
            if (code == "APK_VERIFIED")
                ShowStage(1, 1, "APK conferido", "Localizando o telefone e verificando o USB.", true);
            else if (code == "USB_FOUND")
                ShowStage(1, 1, "Telefone encontrado", "Conferindo se está livre para a atualização.", true);
            else if (code == "PHONE_CHECK")
                ShowStage(1, 1, "Preparando o telefone", "Verificando partida, download e estado do aplicativo.", true);
            else if (code == "INSTALLING")
                ShowStage(2, 2, "Instalando no Android", "Aguarde a confirmação do telefone. Não retire o cabo.", true);
            else if (code == "VERIFYING_PHONE")
                ShowStage(3, 3, "Conferindo a instalação", "Comparando o APK instalado com o pacote assinado.", true);
            return true;
        }

        private bool ShowMeasuredProgress(string line)
        {
            const string marker = "TS_PROGRESS|hash|";
            if (line == null || !line.StartsWith(marker, StringComparison.Ordinal)) return false;
            int percentage;
            if (!Int32.TryParse(line.Substring(marker.Length), out percentage) ||
                percentage < 0 || percentage > 100) return true;
            completedStages = 0;
            activeStage = 0;
            blockedStage = -1;
            stage.Text = currentKind == "install" ? "ETAPA 1 DE 4" : "VERIFICAÇÃO DO PACOTE";
            status.Text = "Conferindo o APK";
            statusDetail.Text = "Lendo o arquivo e comparando o SHA-256.";
            captionBase = "Leitura real do arquivo: " + percentage + "%";
            UpdateElapsed();
            progress.ShowMeasured(percentage, Blue);
            SetActionHint("A instalação no telefone ainda não começou.", Blue);
            UpdateStepLabels();
            return true;
        }

        private void AppendLog(string message)
        {
            if (String.IsNullOrWhiteSpace(message)) return;
            string safe = message;
            foreach (string serial in knownSerials)
            {
                if (!String.IsNullOrWhiteSpace(serial))
                    safe = Regex.Replace(safe, Regex.Escape(serial), "[aparelho]", RegexOptions.IgnoreCase);
            }
            if (log.TextLength > 32000)
                log.Text = log.Text.Substring(Math.Min(log.TextLength, 16000));
            log.AppendText(DateTime.Now.ToString("HH:mm:ss") + "  " + safe + Environment.NewLine);
        }

        private void UpdateButtons()
        {
            bool ready = manifestValid && !busy;
            bool selected = phones.SelectedItem is UsbDevice;
            refresh.Enabled = !busy;
            verify.Enabled = !busy;
            phones.Enabled = ready;
            idleConfirmed.Enabled = ready && selected;
            install.Enabled = ready && selected && idleConfirmed.Checked && !installOutcomeUncertain;
            install.Text = retryAvailable ? "TENTAR NOVAMENTE" : "INSTALAR NO TELEFONE";
            close.Enabled = !busy;
            receipts.Enabled = !busy && Directory.Exists(Path.Combine(folder, "recibos-usb"));
        }

        private void StartRefresh()
        {
            if (busy) return;
            LoadManifest();
            if (!manifestValid) { UpdateButtons(); return; }
            retryAvailable = false;
            phones.Items.Clear();
            knownSerials.Clear();
            idleConfirmed.Checked = false;
            ShowIdle("Buscando telefone", "Procurando aparelhos Android autorizados na porta USB.");
            progress.ShowWorking(Blue);
            captionBase = "Consultando o USB";
            AppendLog("Atualizando a lista de telefones.");
            StartCommand(new CommandRequest { Kind = "list", Arguments = "-ListUsbDevices" });
        }

        private void StartValidation()
        {
            if (busy) return;
            LoadManifest();
            if (!manifestValid) { UpdateButtons(); return; }
            ShowIdle("Conferindo o pacote", "Lendo o APK completo para validar tamanho e SHA-256.");
            AppendLog("Verificando o APK indicado no manifesto.");
            StartCommand(new CommandRequest { Kind = "validate", Arguments = "-ValidateOnly -GuiProgress", StreamOutput = true });
        }

        private void StartInstall()
        {
            if (busy || !manifestValid || !idleConfirmed.Checked || installOutcomeUncertain) return;
            var device = phones.SelectedItem as UsbDevice;
            if (device == null || String.IsNullOrWhiteSpace(device.Serial) ||
                !Regex.IsMatch(device.Serial, "^[A-Za-z0-9._-]{1,128}$"))
            {
                SetStatus("Identificação USB inválida. Atualize a lista e tente novamente.");
                return;
            }
            retryAvailable = false;
            ShowStage(0, 0, "Conferindo o APK", "Validando o arquivo antes de conectar ao telefone.", true);
            AppendLog("Iniciando instalação em " + device.Alias + " — " + device.Model + ".");
            StartCommand(new CommandRequest {
                Kind = "install",
                Arguments = "-DeviceSerial " + Quote(device.Serial) + " -UserConfirmedIdle -GuiProgress",
                StreamOutput = true
            });
        }

        private void StartCommand(CommandRequest request)
        {
            currentKind = request.Kind;
            busy = true;
            elapsed.Restart();
            elapsedTimer.Start();
            if (request.Kind == "validate") progress.ShowWorking(Blue);
            UpdateButtons();
            var worker = new BackgroundWorker();
            worker.WorkerReportsProgress = true;
            worker.DoWork += delegate(object sender, DoWorkEventArgs e)
            {
                var current = (CommandRequest)e.Argument;
                var background = (BackgroundWorker)sender;
                e.Result = RunPowerShell(folder, script, current.Arguments,
                    current.StreamOutput ? (Action<string>)(line => background.ReportProgress(0, line)) : null);
            };
            worker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
            {
                string line = e.UserState as string;
                if (ShowMeasuredProgress(line)) return;
                if (HandleStage(line)) return;
                AppendLog(line);
            };
            worker.RunWorkerCompleted += delegate(object sender, RunWorkerCompletedEventArgs e)
            {
                busy = false;
                elapsedTimer.Stop();
                elapsed.Stop();
                if (e.Error != null)
                {
                    AppendLog("A operação não pôde ser concluída: " + e.Error.Message);
                    ShowBlocked(Math.Max(0, activeStage), completedStages,
                        "Operação interrompida", "Não foi possível concluir a tarefa no computador.",
                        "Consulte os detalhes técnicos e tente novamente.", Red);
                    retryAvailable = request.Kind == "install";
                    if (retryAvailable) idleConfirmed.Checked = false;
                    UpdateButtons();
                    return;
                }
                var result = (CommandResult)e.Result;
                if (request.Kind == "list") FinishRefresh(result);
                else if (request.Kind == "validate") FinishValidation(result);
                else FinishInstall(result);
                UpdateButtons();
            };
            worker.RunWorkerAsync(request);
        }

        private void FinishRefresh(CommandResult result)
        {
            if (result.ExitCode != 0)
            {
                ShowIdle("USB indisponível", "Confira o cabo, desbloqueie o telefone e autorize a depuração.");
                SetActionHint("Nenhum APK foi instalado.", Amber);
                string cause = !String.IsNullOrWhiteSpace(result.Error) ? result.Error : result.Output;
                AppendLog(String.IsNullOrWhiteSpace(cause) ? "A consulta USB falhou." : cause.Trim());
                return;
            }
            try
            {
                var listing = new JavaScriptSerializer().Deserialize<UsbListing>(result.Output.Trim());
                if (listing == null || listing.Authorized == null)
                    throw new InvalidDataException("Lista USB incompleta.");
                foreach (UsbDevice device in listing.Authorized)
                {
                    if (device == null || String.IsNullOrWhiteSpace(device.Serial) ||
                        !Regex.IsMatch(device.Serial, "^[A-Za-z0-9._-]{1,128}$")) continue;
                    knownSerials.Add(device.Serial);
                    phones.Items.Add(device);
                }
                if (phones.Items.Count == 1) phones.SelectedIndex = 0;
                if (phones.Items.Count == 0)
                    ShowIdle("Nenhum telefone autorizado", "Desbloqueie o Android e aceite a depuração USB.");
                else
                    ShowIdle(phones.Items.Count == 1 ? "Telefone encontrado" : "Telefones encontrados",
                        "Selecione um aparelho e confirme que está livre para instalar.");
                if (installOutcomeUncertain)
                    ShowBlocked(2, 2, "Resultado anterior incerto",
                        "Confira no telefone se a atualização terminou.",
                        "Feche e reabra o instalador após conferir este aparelho.", Red);
                if (phones.Items.Count == 0) SetActionHint("Nenhum APK foi instalado.", Amber);
                if (listing.UnauthorizedCount > 0)
                    AppendLog(listing.UnauthorizedCount + " telefone(s) aguardam autorização de depuração USB.");
                if (listing.OfflineCount > 0)
                    AppendLog(listing.OfflineCount + " telefone(s) estão offline; reconecte o cabo.");
                if (listing.ExcludedCount > 0)
                    AppendLog("Conexões de rede, emuladores ou USB não confirmado foram ignorados.");
            }
            catch (Exception)
            {
                ShowIdle("Consulta USB falhou", "A resposta do Android não pôde ser lida. Atualize a lista.");
                SetActionHint("Nenhum APK foi instalado.", Amber);
                AppendLog("A consulta USB retornou dados inesperados.");
            }
        }

        private void FinishValidation(CommandResult result)
        {
            if (result.ExitCode == 0)
            {
                completedStages = 1;
                activeStage = -1;
                blockedStage = -1;
                stage.Text = "VERIFICAÇÃO CONCLUÍDA";
                status.Text = "APK íntegro";
                statusDetail.Text = "Tamanho e SHA-256 conferidos. Escolha o telefone para instalar.";
                progressCaption.Text = "Arquivo conferido  ·  " + elapsed.Elapsed.ToString(@"mm\:ss");
                progress.ShowMeasured(100, Green);
                SetActionHint("Nenhum telefone foi alterado nesta verificação.", Green);
                UpdateStepLabels();
                AppendLog("Arquivo, tamanho e SHA256 conferidos. Nenhum telefone foi alterado.");
            }
            else
            {
                ShowBlocked(0, 0, "APK não conferido", "O pacote não passou na validação de integridade.",
                    "Nenhum APK foi instalado. Consulte os detalhes técnicos.", Red);
                if (!String.IsNullOrWhiteSpace(result.Error)) AppendLog(result.Error.Trim());
            }
        }

        private InstallReceipt ReadInstallReceipt(string output)
        {
            var match = Regex.Match(output ?? "", @"(?m)^Recibo:\s+recibos-usb\\(instalacao-[A-Za-z0-9_-]+\.json)\s*$");
            if (!match.Success) return null;
            try
            {
                string path = Path.Combine(folder, "recibos-usb", match.Groups[1].Value);
                if (!File.Exists(path)) return null;
                return new JavaScriptSerializer().Deserialize<InstallReceipt>(File.ReadAllText(path, Encoding.UTF8));
            }
            catch (Exception error)
            {
                AppendLog("O recibo não pôde ser lido: " + error.Message);
                return null;
            }
        }

        private void ShowInstallFailure(string code, bool attempted)
        {
            if (code == "APP_STILL_IN_FOREGROUND")
                ShowBlocked(1, 1, "TurboStations em outra tela",
                    "Volte à tela inicial do aplicativo ou do Android.",
                    "NENHUM APK FOI INSTALADO. Depois clique em Tentar novamente.", Amber);
            else if (code == "ONLINE_SESSION_NOT_CLOSED" || code == "APP_ACTIVITY_NOT_IDLE")
                ShowBlocked(1, 1, "Partida ainda ativa",
                    "Saia da partida pelo próprio jogo e aguarde o encerramento.",
                    "NENHUM APK FOI INSTALADO.", Amber);
            else if (code == "APP_SERVICE_NOT_CLOSED")
                ShowBlocked(1, 1, "Download ou serviço ativo",
                    "Conclua o download e volte à tela inicial.",
                    "NENHUM APK FOI INSTALADO.", Amber);
            else if (code == "INSTALL_FAILED_INSUFFICIENT_STORAGE")
                ShowBlocked(2, 2, "Espaço insuficiente",
                    "Libere espaço no telefone e tente novamente.",
                    "A instalação não foi concluída. Seus dados foram preservados.", Amber);
            else if (code == "INSTALL_FAILED_UPDATE_INCOMPATIBLE")
                ShowBlocked(2, 2, "Assinatura incompatível",
                    "Este APK usa uma assinatura diferente da versão instalada.",
                    "Corrija a assinatura do pacote; não remova os dados do app.", Red);
            else if (code == "INSTALL_FAILED_VERSION_DOWNGRADE")
                ShowBlocked(2, 2, "Versão inferior detectada",
                    "O Android já possui uma versão mais recente.",
                    "A atualização foi bloqueada para preservar seus dados.", Amber);
            else if (code == "SUCCESS_HASH_MISMATCH" || code == "SUCCESS_HASH_UNVERIFIED")
                ShowBlocked(3, 3, "Instalado, mas não validado",
                    "O Android aceitou o APK; a conferência final falhou.",
                    "Confira o recibo antes de testar ou repetir a instalação.", Red);
            else
                ShowBlocked(attempted ? 2 : 1, attempted ? 2 : 1,
                    attempted ? "Instalação não concluída" : "Preparação interrompida",
                    attempted ? "O Android não confirmou a instalação." : "O telefone não passou nas verificações iniciais.",
                    attempted ? "Confira o recibo antes de repetir." : "NENHUM APK FOI INSTALADO.", Amber);
        }

        private void FinishInstall(CommandResult result)
        {
            var receipt = ReadInstallReceipt(result.Output);
            if (result.ExitCode == 0)
            {
                completedStages = 4;
                activeStage = -1;
                blockedStage = -1;
                stage.Text = "INSTALAÇÃO CONCLUÍDA";
                status.Text = "Pronto para testar";
                statusDetail.Text = "APK instalado e conferido no telefone.";
                progressCaption.Text = "4 de 4 etapas  ·  " + elapsed.Elapsed.ToString(@"mm\:ss");
                progress.ShowMeasured(100, Green);
                SetActionHint("Abra o TurboStations no telefone para conferir a versão.", Green);
                UpdateStepLabels();
                AppendLog("Instalação concluída. Consulte o recibo indicado acima.");
                idleConfirmed.Checked = false;
                retryAvailable = false;
            }
            else
            {
                string code = receipt == null ? "" : receipt.resultCode ?? "";
                bool uncertain = (receipt == null && completedStages >= 2) ||
                    code == "INSTALL_STATUS_UNKNOWN_TIMEOUT" ||
                    (result.Output ?? "").IndexOf("INSTALL_STATUS_UNKNOWN_TIMEOUT", StringComparison.OrdinalIgnoreCase) >= 0;
                if (uncertain)
                {
                    var device = phones.SelectedItem as UsbDevice;
                    if (device != null) uncertainSerial = device.Serial;
                    installOutcomeUncertain = true;
                    ShowBlocked(2, 2, "Resultado da instalação incerto",
                        "A comunicação USB terminou sem confirmação do Android.",
                        "Confira no telefone. Reabra o instalador para decidir uma nova tentativa.", Red);
                }
                else if (receipt != null && receipt.installSuccess &&
                    code != "SUCCESS_HASH_MISMATCH" && code != "SUCCESS_HASH_UNVERIFIED")
                {
                    ShowBlocked(3, 3, "Instalado, confira o recibo",
                        "O Android aceitou o APK, mas a operação terminou com ressalva.",
                        "Não repita antes de conferir a versão no telefone.", Amber);
                    retryAvailable = false;
                    idleConfirmed.Checked = false;
                    return;
                }
                else ShowInstallFailure(code, receipt == null ? completedStages >= 2 : receipt.installAttempted);
                if (!String.IsNullOrWhiteSpace(result.Error)) AppendLog(result.Error.Trim());
                retryAvailable = !uncertain;
                idleConfirmed.Checked = false;
            }
        }
    }

    private static string Quote(string value)
    {
        return "\"" + value.Replace("\"", "\\\"") + "\"";
    }

    private static void WriteUtf8(bool toError, string value)
    {
        if (String.IsNullOrEmpty(value)) return;
        try
        {
            using (Stream stream = toError ? Console.OpenStandardError() : Console.OpenStandardOutput())
            {
                byte[] bytes = new UTF8Encoding(false).GetBytes(value);
                stream.Write(bytes, 0, bytes.Length);
                stream.Flush();
            }
        }
        catch (IOException)
        {
            if (toError) Console.Error.Write(value);
            else Console.Out.Write(value);
        }
    }

    private static CommandResult RunPowerShell(string folder, string script, string arguments, Action<string> onLine)
    {
        string executable = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),
            "WindowsPowerShell", "v1.0", "powershell.exe");
        if (!File.Exists(executable))
            throw new FileNotFoundException("Windows PowerShell não encontrado.", executable);
        var start = new ProcessStartInfo();
        start.FileName = executable;
        start.Arguments = "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File " +
                          Quote(script) + " " + arguments;
        start.WorkingDirectory = folder;
        start.UseShellExecute = false;
        start.CreateNoWindow = true;
        start.RedirectStandardOutput = true;
        start.RedirectStandardError = true;
        // Some Windows environments expose both Path and PATH. Accessing the .NET Framework
        // StringDictionary would then throw before PowerShell starts; inheritance is sufficient.
        Environment.SetEnvironmentVariable("TS_USB_INSTALLER_UTF8", "1", EnvironmentVariableTarget.Process);
        start.StandardOutputEncoding = new UTF8Encoding(false);
        start.StandardErrorEncoding = new UTF8Encoding(false);
        var output = new StringBuilder();
        var error = new StringBuilder();
        var outputLock = new object();
        bool installing = arguments.IndexOf("-DeviceSerial", StringComparison.OrdinalIgnoreCase) >= 0;
        int timeoutMs = installing ? 36 * 60 * 1000 :
            arguments.IndexOf("-ValidateOnly", StringComparison.OrdinalIgnoreCase) >= 0 ? 15 * 60 * 1000 : 2 * 60 * 1000;
        using (var stdoutClosed = new ManualResetEvent(false))
        using (var stderrClosed = new ManualResetEvent(false))
        using (var process = new Process())
        {
            process.StartInfo = start;
            process.OutputDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (e.Data == null) { stdoutClosed.Set(); return; }
                lock (outputLock) { output.AppendLine(e.Data); }
                if (onLine != null) onLine(e.Data);
            };
            process.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs e)
            {
                if (e.Data == null) { stderrClosed.Set(); return; }
                lock (outputLock) { error.AppendLine(e.Data); }
                if (onLine != null) onLine(e.Data);
            };
            if (!process.Start()) throw new InvalidOperationException("Não foi possível iniciar o instalador.");
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
            if (!process.WaitForExit(timeoutMs))
            {
                try { process.Kill(); process.WaitForExit(5000); } catch (InvalidOperationException) { }
                return new CommandResult {
                    ExitCode = 124,
                    Output = installing ? "INSTALL_STATUS_UNKNOWN_TIMEOUT" : "OPERATION_TIMEOUT",
                    Error = "A operação excedeu o tempo limite. Confira o telefone antes de repetir."
                };
            }
            if (!stdoutClosed.WaitOne(5000) || !stderrClosed.WaitOne(5000))
            {
                return new CommandResult {
                    ExitCode = 124,
                    Output = installing ? "INSTALL_STATUS_UNKNOWN_TIMEOUT" : "OPERATION_TIMEOUT",
                    Error = "A saída do instalador não terminou. Confira o telefone antes de repetir."
                };
            }
            return new CommandResult { ExitCode = process.ExitCode, Output = output.ToString(), Error = error.ToString() };
        }
    }

    [STAThread]
    private static int Main(string[] args)
    {
        bool validateOnly = args.Length == 1 && args[0] == "--validate";
        bool listOnly = args.Length == 1 && args[0] == "--list";
        if (args.Length != 0 && !validateOnly && !listOnly) return 2;
        string folder = AppDomain.CurrentDomain.BaseDirectory;
        string script = Path.Combine(folder, "Instalar-TurboStations-USB.ps1");
        string manifest = Path.Combine(folder, "turbostations-apk-teste.json");
        if (!File.Exists(script) || !File.Exists(manifest))
        {
            const string missing = "Instalador PowerShell ou manifesto ausente ao lado do EXE.";
            if (validateOnly || listOnly) WriteUtf8(true, missing + Environment.NewLine);
            else MessageBox.Show(missing, "TurboStations — instalador USB",
                MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 2;
        }
        if (validateOnly || listOnly)
        {
            try
            {
                CommandResult result = RunPowerShell(folder, script,
                    validateOnly ? "-ValidateOnly" : "-ListUsbDevices", null);
                WriteUtf8(false, result.Output);
                WriteUtf8(true, result.Error);
                return result.ExitCode;
            }
            catch (Exception error)
            {
                WriteUtf8(true, "Não foi possível concluir a verificação: " + error.Message + Environment.NewLine);
                return 2;
            }
        }
        bool firstInstance;
        using (var instance = new Mutex(true, "Local\\TurboStationsUsbInstallerGui", out firstInstance))
        {
            if (!firstInstance)
            {
                MessageBox.Show("O instalador já está aberto. Use a janela existente.",
                    "TurboStations — instalador USB", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return 1;
            }
            try
            {
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(new InstallerForm(folder, script, manifest));
            }
            finally { instance.ReleaseMutex(); }
        }
        return 0;
    }
}
