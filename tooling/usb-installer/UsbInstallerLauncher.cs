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
        public string appServiceCheck { get; set; }
        public string appActivityCheck { get; set; }
        public bool installAttempted { get; set; }
        public bool installSuccess { get; set; }
        public string deviceModel { get; set; }
    }

    private sealed class InstallResultSignal
    {
        public string Code;
        public bool Installed;
        public bool HashVerified;
        public bool ReceiptSaved;
    }

    private sealed class DashboardProgressBar : Control
    {
        private readonly System.Windows.Forms.Timer animation = new System.Windows.Forms.Timer();
        private int value;
        private int lastMeasured;
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
            lastMeasured = value;
            accent = color;
            Invalidate();
        }

        public int LastMeasuredPercentage { get { return lastMeasured; } }

        public void StopAtLastMeasured(Color color)
        {
            animation.Stop();
            indeterminate = false;
            value = lastMeasured;
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
            using (var background = new SolidBrush(Color.FromArgb(217, 228, 240)))
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
        private static readonly Color Canvas = Color.FromArgb(244, 247, 251);
        private static readonly Color Surface = Color.White;
        private static readonly Color SurfaceRaised = Color.FromArgb(239, 244, 250);
        private static readonly Color Ink = Color.FromArgb(25, 42, 62);
        private static readonly Color Muted = Color.FromArgb(77, 95, 115);
        private static readonly Color Blue = Color.FromArgb(15, 94, 174);
        private static readonly Color Green = Color.FromArgb(20, 116, 75);
        private static readonly Color Amber = Color.FromArgb(151, 91, 11);
        private static readonly Color Red = Color.FromArgb(181, 48, 51);
        private readonly string folder;
        private readonly string script;
        private readonly string manifestFile;
        private readonly Panel header = new Panel();
        private readonly Panel packageCard = new Panel();
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
        private readonly Label packageHeading = new Label();
        private readonly Label packageTitle = new Label();
        private readonly Label packageDetail = new Label();
        private readonly Label packageBadge = new Label();
        private readonly Label devicesHeading = new Label();
        private readonly Label deviceEmpty = new Label();
        private readonly Label stage = new Label();
        private readonly Label status = new Label();
        private readonly Label statusDetail = new Label();
        private readonly Label progressCaption = new Label();
        private readonly Label actionHint = new Label();
        private readonly Label[] stepLabels = new Label[4];
        private readonly ComboBox phones = new ComboBox();
        private readonly CheckBox idleConfirmed = new CheckBox();
        private readonly Button refresh = new Button();
        private readonly Button install = new Button();
        private readonly Button verify = new Button();
        private readonly Button close = new Button();
        private readonly DashboardProgressBar progress = new DashboardProgressBar();
        private readonly DashboardProgressBar packageProgress = new DashboardProgressBar();
        private readonly TextBox log = new TextBox();
        private TextBox liveDetails;
        private readonly LinkLabel receipts = new LinkLabel();
        private readonly LinkLabel details = new LinkLabel();
        private readonly List<string> knownSerials = new List<string>();
        private readonly Stopwatch elapsed = new Stopwatch();
        private readonly System.Windows.Forms.Timer elapsedTimer = new System.Windows.Forms.Timer();
        private readonly System.Windows.Forms.Timer packageTimer = new System.Windows.Forms.Timer();
        private FileSystemWatcher packageWatcher;
        private Manifest packageManifest;
        private string packageApk;
        private string verifiedStamp;
        private string failedStamp;
        private string validationStamp;
        private string packageStateKey;
        private bool packageNeedsVerification;
        private bool directCopyPending;
        private DateTime lastPackageChangeUtc;
        private long lastQueuedPackageEventTicks;
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
            MinimumSize = new Size(760, 600);
            ClientSize = new Size(900, 660);
            AutoScroll = true;

            header.BackColor = Surface;
            brandMark.BackColor = Blue;
            brandLetter.Text = "T";
            brandLetter.Font = new Font("Segoe UI Semibold", 19F, FontStyle.Bold);
            brandLetter.ForeColor = Color.White;
            brandLetter.TextAlign = ContentAlignment.MiddleCenter;
            brandMark.Controls.Add(brandLetter);
            title.Text = "TurboStations";
            title.ForeColor = Ink;
            title.Font = new Font("Segoe UI Semibold", 19F, FontStyle.Bold);
            version.ForeColor = Blue;
            version.Font = new Font("Segoe UI Semibold", 8.5F, FontStyle.Bold);
            candidate.Text = "VERSÃO DE TESTE";
            candidate.TextAlign = ContentAlignment.MiddleCenter;
            candidate.BackColor = Surface;
            candidate.ForeColor = Amber;
            candidate.Font = new Font("Segoe UI Semibold", 8F, FontStyle.Bold);
            warning.ForeColor = Muted;
            warning.Font = new Font("Segoe UI", 8.7F);
            warning.AutoEllipsis = true;
            header.Controls.AddRange(new Control[] { brandMark, title, version, candidate, warning });

            packageCard.BackColor = Surface;
            packageHeading.Text = "ARQUIVO DE INSTALAÇÃO";
            packageHeading.ForeColor = Muted;
            packageHeading.Font = new Font("Segoe UI Semibold", 8.5F, FontStyle.Bold);
            packageTitle.ForeColor = Ink;
            packageTitle.Font = new Font("Segoe UI Semibold", 12.5F, FontStyle.Bold);
            packageTitle.AutoEllipsis = true;
            packageDetail.ForeColor = Muted;
            packageDetail.Font = new Font("Segoe UI", 9F);
            packageDetail.AutoEllipsis = true;
            packageBadge.TextAlign = ContentAlignment.MiddleCenter;
            packageBadge.Font = new Font("Segoe UI Semibold", 8.5F, FontStyle.Bold);
            packageCard.Controls.AddRange(new Control[] {
                packageHeading, packageTitle, packageDetail, packageBadge, packageProgress
            });

            deviceCard.BackColor = Surface;
            devicesHeading.Text = "TELEFONE USB";
            devicesHeading.ForeColor = Muted;
            devicesHeading.Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold);
            refresh.Text = "ATUALIZAR USB";
            StyleSecondaryButton(refresh);
            refresh.Click += delegate { StartRefresh(); };
            phones.BackColor = SurfaceRaised;
            phones.ForeColor = Ink;
            phones.DrawMode = DrawMode.OwnerDrawFixed;
            phones.ItemHeight = 43;
            phones.DrawItem += DrawPhone;
            phones.IntegralHeight = false;
            phones.DropDownStyle = ComboBoxStyle.DropDownList;
            phones.MaxDropDownItems = 6;
            deviceEmpty.Text = "Buscando aparelhos conectados…";
            deviceEmpty.ForeColor = Muted;
            deviceEmpty.BackColor = SurfaceRaised;
            deviceEmpty.Font = new Font("Segoe UI", 9.5F);
            deviceEmpty.TextAlign = ContentAlignment.MiddleLeft;
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
            deviceCard.Controls.AddRange(new Control[] { devicesHeading, refresh, phones, deviceEmpty });

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
            actionHint.BackColor = Surface;
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
                header, packageCard, deviceCard, confirmationCard, operationCard,
                actionRow, details, receipts
            });
            Resize += delegate { LayoutDashboard(); };
            elapsedTimer.Interval = 1000;
            elapsedTimer.Tick += delegate { UpdateElapsed(); };
            packageTimer.Interval = 1000;
            packageTimer.Tick += delegate { RefreshPackageState(); };
            FormClosing += OnFormClosing;
            FormClosed += delegate {
                elapsedTimer.Stop();
                packageTimer.Stop();
                elapsedTimer.Dispose();
                packageTimer.Dispose();
                if (packageWatcher != null) packageWatcher.Dispose();
            };
            Shown += delegate { BeginInvoke(new Action(StartRefresh)); };
            LayoutDashboard();
            ShowIdle("Aguardando telefone", "Conecte um aparelho por USB e autorize a depuração.");
            LoadManifest();
            StartPackageWatcher();
            UpdateButtons();
        }

        private static void StyleSecondaryButton(Button button)
        {
            button.FlatStyle = FlatStyle.Flat;
            button.FlatAppearance.BorderSize = 1;
            button.FlatAppearance.BorderColor = Color.FromArgb(192, 208, 225);
            button.BackColor = Surface;
            button.ForeColor = Blue;
            button.Font = new Font("Segoe UI Semibold", 9F, FontStyle.Bold);
            button.Cursor = Cursors.Hand;
            button.UseVisualStyleBackColor = false;
        }

        private static void StylePrimaryButton(Button button)
        {
            button.FlatStyle = FlatStyle.Flat;
            button.FlatAppearance.BorderSize = 0;
            button.BackColor = Blue;
            button.ForeColor = Color.White;
            button.Font = new Font("Segoe UI Semibold", 10F, FontStyle.Bold);
            button.Cursor = Cursors.Hand;
            button.UseVisualStyleBackColor = false;
        }

        private void LayoutDashboard()
        {
            float scale;
            using (var graphics = CreateGraphics()) scale = graphics.DpiX / 96F;
            Func<int, int> u = value => (int)Math.Round(value * scale);
            int width = Math.Max(ClientSize.Width, u(850));
            int height = Math.Max(ClientSize.Height, u(660));
            header.SetBounds(0, 0, width, u(94));
            brandMark.SetBounds(u(24), u(16), u(50), u(50));
            brandLetter.Dock = DockStyle.Fill;
            title.SetBounds(u(91), u(11), Math.Max(u(200), width - u(300)), u(36));
            version.SetBounds(u(92), u(49), Math.Max(u(200), width - u(300)), u(19));
            candidate.SetBounds(width - u(177), u(22), u(153), u(27));
            warning.SetBounds(u(24), u(70), width - u(48), u(19));

            int cardWidth = width - u(48);
            packageCard.SetBounds(u(24), u(105), cardWidth, u(105));
            packageHeading.SetBounds(u(20), u(9), cardWidth - u(175), u(20));
            packageTitle.SetBounds(u(20), u(29), cardWidth - u(193), u(26));
            packageDetail.SetBounds(u(20), u(56), cardWidth - u(40), u(20));
            packageBadge.SetBounds(cardWidth - u(176), u(15), u(156), u(27));
            packageProgress.SetBounds(u(20), u(84), cardWidth - u(40), u(9));

            deviceCard.SetBounds(u(24), u(220), cardWidth, u(99));
            devicesHeading.SetBounds(u(20), u(9), cardWidth - u(205), u(27));
            refresh.SetBounds(cardWidth - u(172), u(10), u(152), u(31));
            phones.SetBounds(u(20), u(45), cardWidth - u(40), u(44));
            deviceEmpty.SetBounds(u(20), u(45), cardWidth - u(40), u(44));
            confirmationCard.SetBounds(u(24), u(329), cardWidth, u(45));
            idleConfirmed.SetBounds(u(18), u(5), cardWidth - u(36), u(35));

            int operationBottom = height - u(97);
            operationCard.SetBounds(u(24), u(384), cardWidth,
                Math.Max(u(172), operationBottom - u(384)));
            stage.SetBounds(u(20), u(8), cardWidth - u(40), u(19));
            status.SetBounds(u(20), u(30), cardWidth - u(40), u(34));
            statusDetail.SetBounds(u(20), u(65), cardWidth - u(40), u(22));
            progressCaption.SetBounds(u(20), u(89), cardWidth - u(40), u(18));
            progress.SetBounds(u(20), u(110), cardWidth - u(40), u(10));
            actionHint.SetBounds(u(20), u(124), cardWidth - u(40), u(20));
            int chipsTop = operationCard.Height - u(24);
            int gap = u(7);
            int chipWidth = (cardWidth - u(40) - gap * 3) / 4;
            for (int i = 0; i < stepLabels.Length; i++)
                stepLabels[i].SetBounds(u(20) + i * (chipWidth + gap), chipsTop, chipWidth, u(20));

            actionRow.SetBounds(u(24), height - u(87), cardWidth, u(46));
            int primaryWidth = Math.Min(u(330), Math.Max(u(250), cardWidth / 2 - u(35)));
            install.SetBounds(0, 0, primaryWidth, u(44));
            verify.SetBounds(primaryWidth + u(12), 0, u(160), u(44));
            close.SetBounds(cardWidth - u(126), 0, u(126), u(44));
            details.SetBounds(u(24), height - u(30), u(166), u(21));
            receipts.SetBounds(u(208), height - u(30), u(140), u(21));
            AutoScrollMinSize = new Size(width, height);
        }

        private void DrawPhone(object sender, DrawItemEventArgs e)
        {
            if (e.Index < 0 || e.Index >= phones.Items.Count) return;
            var device = phones.Items[e.Index] as UsbDevice;
            if (device == null) return;
            bool selected = (e.State & DrawItemState.Selected) == DrawItemState.Selected;
            using (var background = new SolidBrush(selected ? Color.FromArgb(218, 235, 250) : SurfaceRaised))
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
            if (liveDetails != null && !liveDetails.IsDisposed)
            {
                liveDetails.FindForm().Activate();
                return;
            }
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
            liveDetails = copy;
            window.FormClosed += delegate { liveDetails = null; };
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
            actionHint.BackColor = Surface;
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
                label.BackColor = Surface;
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
            // Four milestones do not represent a measured ADB transfer percentage.
            progress.StopAtLastMeasured(color);
            if (progress.LastMeasuredPercentage > 0)
                progressCaption.Text = "Leitura do APK: " + progress.LastMeasuredPercentage + "%";
            SetActionHint(hint, color);
            UpdateStepLabels();
        }

        private static string FileStamp(string apk, Manifest manifest)
        {
            var file = new FileInfo(apk);
            return apk.ToUpperInvariant() + "|" + file.Length + "|" +
                file.LastWriteTimeUtc.Ticks + "|" + manifest.sha256.ToUpperInvariant();
        }

        private bool TryCompleteApk(out string stamp)
        {
            stamp = null;
            try
            {
                if (directCopyPending || packageManifest == null || String.IsNullOrWhiteSpace(packageApk) ||
                    File.Exists(packageApk + ".partial") || !File.Exists(packageApk) ||
                    new FileInfo(packageApk).Length != packageManifest.bytes) return false;
                // A copy may preallocate its final length. Require the writer to have
                // released the file before any hash or installation can start.
                using (var unlocked = new FileStream(packageApk, FileMode.Open,
                    FileAccess.Read, FileShare.None)) { }
                stamp = FileStamp(packageApk, packageManifest);
                return true;
            }
            catch (IOException) { return false; }
            catch (UnauthorizedAccessException) { return false; }
        }

        private void SetPackageState(string key, string heading, string detail,
            string badge, Color accent, bool working, bool complete)
        {
            if (packageStateKey == key) return;
            packageStateKey = key;
            packageTitle.Text = heading;
            packageDetail.Text = detail;
            packageBadge.Text = badge;
            packageBadge.ForeColor = accent;
            packageBadge.BackColor = Surface;
            if (working) packageProgress.ShowWorking(accent);
            else packageProgress.ShowMeasured(complete ? 100 : 0, accent);
        }

        private void LoadManifest()
        {
            manifestValid = false;
            packageNeedsVerification = false;
            packageManifest = null;
            packageApk = null;
            try
            {
                if (!File.Exists(manifestFile))
                    throw new FileNotFoundException("Arquivo de controle ausente: " +
                        Path.GetFileName(manifestFile));
                var manifest = new JavaScriptSerializer().Deserialize<Manifest>(
                    File.ReadAllText(manifestFile, Encoding.UTF8));
                if (manifest == null || String.IsNullOrWhiteSpace(manifest.revision))
                    throw new InvalidDataException("O arquivo de controle não informa a revisão.");
                if (String.IsNullOrWhiteSpace(manifest.apkPath) ||
                    !Regex.IsMatch(manifest.sha256 ?? "", "^[a-fA-F0-9]{64}$") || manifest.bytes <= 0)
                    throw new InvalidDataException("O arquivo de controle não informa APK, tamanho e SHA-256 válidos.");
                string apk = Path.IsPathRooted(manifest.apkPath) ? manifest.apkPath :
                    Path.Combine(folder, manifest.apkPath);
                packageManifest = manifest;
                packageApk = apk;
                candidate.Visible = true;
                version.Text = "INSTALADOR USB  /  " + manifest.revision.ToUpperInvariant();
                warning.Text = String.IsNullOrWhiteSpace(manifest.warning) ?
                    "Atualização de teste · seus dados são preservados · instale um telefone por vez" :
                    manifest.warning;
                packageHeading.Text = "ARQUIVO DE INSTALAÇÃO  ·  " + manifest.revision.ToUpperInvariant();
                string name = Path.GetFileName(apk);
                bool partial = File.Exists(apk + ".partial");
                if (partial || directCopyPending)
                {
                    packageTimer.Start();
                    SetPackageState("copying|" + name + "|" + partial,
                        "Recebendo o APK", partial ?
                            "Cópia temporária: " + name + ".partial · aguarde a conclusão." :
                            "Cópia em andamento: " + name + " · aguardando o arquivo fechar.",
                        "CÓPIA EM ANDAMENTO", Blue, true, false);
                    return;
                }
                packageTimer.Stop();
                if (!File.Exists(apk))
                {
                    SetPackageState("missing|" + name,
                        "APK não encontrado", "Arquivo esperado nesta pasta: " + name,
                        "ARQUIVO AUSENTE", Amber, false, false);
                    return;
                }
                var file = new FileInfo(apk);
                if (file.Length != manifest.bytes)
                {
                    SetPackageState("size|" + name + "|" + file.Length,
                        "Arquivo incompleto ou incorreto", "Esperado: " + name +
                        " · tamanho diferente do pacote oficial.",
                        "INSTALAÇÃO BLOQUEADA", Red, false, false);
                    return;
                }
                string stamp = FileStamp(apk, manifest);
                if (String.Equals(stamp, verifiedStamp, StringComparison.Ordinal))
                {
                    manifestValid = true;
                    SetPackageState("ready|" + stamp, "APK íntegro e pronto",
                        name + " · tamanho e SHA-256 conferidos.",
                        "VERIFICADO", Green, false, true);
                }
                else if (String.Equals(stamp, failedStamp, StringComparison.Ordinal))
                    SetPackageState("failed|" + stamp, "APK não passou na conferência",
                        name + " · confira a cópia e tente Verificar APK novamente.",
                        "INSTALAÇÃO BLOQUEADA", Red, false, false);
                else
                {
                    packageNeedsVerification = true;
                    SetPackageState("pending|" + stamp, "Conferência necessária",
                        name + " · aguardando leitura completa do SHA-256.",
                        "AGUARDANDO VERIFICAÇÃO", Blue, false, false);
                }
            }
            catch (Exception error)
            {
                packageTimer.Stop();
                version.Text = "INSTALADOR USB  /  SEM PACOTE";
                candidate.Visible = false;
                warning.Text = "Conecte um pacote completo para iniciar a instalação.";
                packageHeading.Text = "ARQUIVO DE INSTALAÇÃO";
                SetPackageState("manifest|" + error.Message, "Pacote indisponível", error.Message,
                    "INSTALAÇÃO BLOQUEADA", Red, false, false);
            }
            finally { UpdateButtons(); }
        }

        private void RefreshPackageState()
        {
            if (busy) return;
            if (directCopyPending)
            {
                if (DateTime.UtcNow - lastPackageChangeUtc < TimeSpan.FromSeconds(2)) return;
                try
                {
                    if (!File.Exists(packageApk)) directCopyPending = false;
                    else using (var unlocked = new FileStream(packageApk, FileMode.Open,
                        FileAccess.Read, FileShare.None)) { directCopyPending = false; }
                }
                catch (IOException) { return; }
                catch (UnauthorizedAccessException) { return; }
            }
            LoadManifest();
            TryAutoValidate();
        }

        private void TryAutoValidate()
        {
            string stamp;
            if (busy || !packageNeedsVerification || !TryCompleteApk(out stamp) ||
                String.Equals(stamp, failedStamp, StringComparison.Ordinal)) return;
            StartValidation();
        }

        private void StartPackageWatcher()
        {
            try
            {
                packageWatcher = new FileSystemWatcher(folder);
                packageWatcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite;
                packageWatcher.Created += delegate(object sender, FileSystemEventArgs e) {
                    PackageFileChanged(e.Name, e.ChangeType);
                };
                packageWatcher.Changed += delegate(object sender, FileSystemEventArgs e) {
                    PackageFileChanged(e.Name, e.ChangeType);
                };
                packageWatcher.Deleted += delegate(object sender, FileSystemEventArgs e) {
                    PackageFileChanged(e.Name, e.ChangeType);
                };
                packageWatcher.Renamed += delegate(object sender, RenamedEventArgs e) {
                    PackageFileChanged(e.Name, e.ChangeType);
                };
                packageWatcher.Error += delegate {
                    try
                    {
                        if (!IsDisposed && IsHandleCreated)
                            BeginInvoke(new Action(delegate {
                                if (packageWatcher != null) packageWatcher.Dispose();
                                packageWatcher = null;
                                LoadManifest();
                                AppendLog("A unidade do pacote deixou de responder. Reconecte-a e clique em Atualizar USB.");
                            }));
                    }
                    catch (InvalidOperationException) { }
                };
                packageWatcher.EnableRaisingEvents = true;
            }
            catch (IOException) { packageWatcher = null; }
            catch (UnauthorizedAccessException) { packageWatcher = null; }
        }

        private void PackageFileChanged(string name, WatcherChangeTypes kind)
        {
            if (String.IsNullOrWhiteSpace(name)) return;
            string expected = packageApk == null ? "" : Path.GetFileName(packageApk);
            if (!String.Equals(name, Path.GetFileName(manifestFile), StringComparison.OrdinalIgnoreCase) &&
                !String.Equals(name, expected, StringComparison.OrdinalIgnoreCase) &&
                !String.Equals(name, expected + ".partial", StringComparison.OrdinalIgnoreCase)) return;
            if (kind == WatcherChangeTypes.Changed)
            {
                long now = DateTime.UtcNow.Ticks;
                long previous = Interlocked.Read(ref lastQueuedPackageEventTicks);
                if (now - previous < TimeSpan.FromMilliseconds(600).Ticks) return;
                Interlocked.Exchange(ref lastQueuedPackageEventTicks, now);
            }
            try
            {
                if (!IsDisposed && IsHandleCreated)
                    BeginInvoke(new Action(delegate {
                        if (String.Equals(name, expected, StringComparison.OrdinalIgnoreCase))
                        {
                            directCopyPending = kind == WatcherChangeTypes.Created ||
                                kind == WatcherChangeTypes.Changed;
                            lastPackageChangeUtc = DateTime.UtcNow;
                            if (directCopyPending) packageTimer.Start();
                        }
                        RefreshPackageState();
                    }));
            }
            catch (InvalidOperationException) { }
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
            packageTitle.Text = "Conferindo a integridade do APK";
            packageDetail.Text = "Lidos " + percentage + "% dos bytes para calcular o SHA-256.";
            packageBadge.Text = percentage + "% LIDO";
            packageBadge.ForeColor = Blue;
            packageProgress.ShowMeasured(percentage, Blue);
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
            if (liveDetails != null && !liveDetails.IsDisposed)
            {
                liveDetails.Text = log.Text;
                liveDetails.SelectionStart = liveDetails.TextLength;
                liveDetails.ScrollToCaret();
            }
        }

        private void UpdateButtons()
        {
            bool ready = manifestValid && !busy;
            bool selected = phones.SelectedItem is UsbDevice;
            string availableStamp;
            refresh.Enabled = !busy;
            verify.Enabled = !busy && TryCompleteApk(out availableStamp);
            phones.Enabled = !busy && phones.Items.Count > 0;
            // Keep the instruction readable even while the APK or USB is unavailable.
            // The install action itself remains gated by package, device and confirmation.
            idleConfirmed.Enabled = true;
            idleConfirmed.ForeColor = Ink;
            install.Enabled = ready && selected && idleConfirmed.Checked && !installOutcomeUncertain;
            install.BackColor = install.Enabled ? Blue : Color.FromArgb(216, 226, 238);
            install.ForeColor = install.Enabled ? Color.White : Color.FromArgb(88, 105, 122);
            install.Text = retryAvailable ? "TENTAR NOVAMENTE" : "INSTALAR NO TELEFONE";
            phones.Visible = phones.Items.Count > 0;
            deviceEmpty.Visible = phones.Items.Count == 0;
            deviceEmpty.BringToFront();
            close.Enabled = !busy;
            receipts.Enabled = !busy && Directory.Exists(Path.Combine(folder, "recibos-usb"));
        }

        private void StartRefresh()
        {
            if (busy) return;
            if (packageWatcher == null) StartPackageWatcher();
            LoadManifest();
            retryAvailable = false;
            phones.Items.Clear();
            deviceEmpty.Text = "Buscando telefones USB autorizados…";
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
            string availableStamp;
            if (!TryCompleteApk(out availableStamp))
            {
                UpdateButtons();
                return;
            }
            packageNeedsVerification = false;
            validationStamp = availableStamp;
            SetPackageState("checking|" + validationStamp,
                "Conferindo a integridade do APK", "Lendo o arquivo completo para validar o SHA-256.",
                "VERIFICANDO", Blue, true, false);
            ShowIdle("Conferindo o pacote", "Lendo o APK completo para validar tamanho e SHA-256.");
            AppendLog("Verificando o APK indicado no manifesto.");
            StartCommand(new CommandRequest { Kind = "validate", Arguments = "-ValidateOnly -GuiProgress", StreamOutput = true });
        }

        private void StartInstall()
        {
            if (busy || !idleConfirmed.Checked || installOutcomeUncertain) return;
            LoadManifest();
            if (!manifestValid) return;
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
                if (request.Kind == "list")
                {
                    LoadManifest();
                    TryAutoValidate();
                }
            };
            worker.RunWorkerAsync(request);
        }

        private void FinishRefresh(CommandResult result)
        {
            if (result.ExitCode != 0)
            {
                ShowIdle("USB indisponível", "Confira o cabo e a autorização da depuração USB.");
                deviceEmpty.Text = "Não foi possível consultar o USB. Confira o cabo e tente Atualizar USB.";
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
                {
                    if (listing.UnauthorizedCount > 0)
                    {
                        ShowIdle("Depuração USB não autorizada", "Desbloqueie o telefone e aceite a autorização deste computador.");
                        deviceEmpty.Text = "Aguardando autorização de depuração USB no telefone.";
                    }
                    else if (listing.OfflineCount > 0)
                    {
                        ShowIdle("Telefone USB desconectado", "Reconecte o cabo e mantenha a tela desbloqueada.");
                        deviceEmpty.Text = "Telefone offline. Reconecte o cabo USB.";
                    }
                    else
                    {
                        ShowIdle("Nenhum telefone encontrado", "Conecte um Android por USB e autorize a depuração.");
                        deviceEmpty.Text = "Nenhum telefone autorizado por USB. Conecte e desbloqueie o aparelho.";
                    }
                    if (!manifestValid) stage.Text = "AGUARDANDO PACOTE";
                }
                else
                {
                    ShowIdle(phones.Items.Count == 1 ? "Telefone encontrado" : "Telefones encontrados",
                        manifestValid ? "Confirme que o aparelho está livre para instalar." :
                            "Telefone pronto; falta receber e conferir o APK mostrado acima.");
                    if (!manifestValid)
                    {
                        stage.Text = "AGUARDANDO APK";
                        status.Text = phones.Items.Count == 1 ? "Telefone conectado" : "Telefones conectados";
                        SetActionHint("A instalação fica disponível após conferir o APK.", Amber);
                    }
                }
                devicesHeading.Text = phones.Items.Count > 1 ?
                    "TELEFONES USB · " + phones.Items.Count + " DISPONÍVEIS" : "TELEFONE USB";
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
                deviceEmpty.Text = "O computador não conseguiu ler a lista USB. Clique em Atualizar USB.";
                SetActionHint("Nenhum APK foi instalado.", Amber);
                AppendLog("A consulta USB retornou dados inesperados.");
            }
        }

        private void FinishValidation(CommandResult result)
        {
            string currentStamp;
            bool sameFile = TryCompleteApk(out currentStamp) &&
                String.Equals(currentStamp, validationStamp, StringComparison.Ordinal);
            if (result.ExitCode == 0 && sameFile)
            {
                verifiedStamp = validationStamp;
                failedStamp = null;
                LoadManifest();
                completedStages = 1;
                activeStage = -1;
                blockedStage = -1;
                stage.Text = "VERIFICAÇÃO CONCLUÍDA";
                status.Text = "APK íntegro";
                statusDetail.Text = "Tamanho e SHA-256 conferidos. Confirme que o telefone está livre.";
                progressCaption.Text = "Arquivo conferido  ·  " + elapsed.Elapsed.ToString(@"mm\:ss");
                progress.ShowMeasured(100, Green);
                SetActionHint("Nenhum telefone foi alterado nesta verificação.", Green);
                UpdateStepLabels();
                AppendLog("Arquivo, tamanho e SHA256 conferidos. Nenhum telefone foi alterado.");
            }
            else
            {
                verifiedStamp = null;
                failedStamp = sameFile ? validationStamp : null;
                LoadManifest();
                ShowBlocked(0, 0, "APK não conferido",
                    sameFile ? "O SHA-256 não corresponde ao pacote esperado." :
                        "O arquivo mudou durante a leitura; confira a cópia e repita.",
                    "Nenhum APK foi instalado. Confira o arquivo esperado acima.", Red);
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

        private static InstallResultSignal ReadResultSignal(string output)
        {
            var match = Regex.Match(output ?? "",
                @"(?m)^TS_RESULT\|([A-Z0-9_]+)\|([01])\|([01])\|([01])\s*$",
                RegexOptions.CultureInvariant);
            if (!match.Success) return null;
            return new InstallResultSignal {
                Code = match.Groups[1].Value,
                Installed = match.Groups[2].Value == "1",
                HashVerified = match.Groups[3].Value == "1",
                ReceiptSaved = match.Groups[4].Value == "1"
            };
        }

        private void ShowInstallFailure(string code, bool attempted, InstallReceipt receipt)
        {
            if (code == "ONLINE_SESSION_CHECK_UNAVAILABLE" ||
                code == "APP_SERVICE_CHECK_UNAVAILABLE" ||
                code == "APP_ACTIVITY_CHECK_UNAVAILABLE")
                ShowBlocked(1, 1, "Checagem do telefone indisponível",
                    "O Android não respondeu à verificação de segurança. Reconecte o USB e tente novamente.",
                    "NENHUM APK FOI INSTALADO.", Amber);
            else if (code == "APP_STILL_IN_FOREGROUND")
                ShowBlocked(1, 1, "TurboStations em outra tela",
                    "Volte à tela inicial do aplicativo ou do Android.",
                    "NENHUM APK FOI INSTALADO. Depois clique em Tentar novamente.", Amber);
            else if (code == "ONLINE_SESSION_NOT_CLOSED" || code == "APP_ACTIVITY_NOT_IDLE")
            {
                bool unavailable = receipt != null && receipt.appActivityCheck == "APP_ACTIVITY_CHECK_UNAVAILABLE";
                ShowBlocked(1, 1, unavailable ? "Checagem do telefone indisponível" : "Partida ainda ativa",
                    unavailable ? "Não foi possível confirmar se o jogo fechou. Reconecte o USB e tente novamente." :
                        "Saia da partida pelo próprio jogo e aguarde o encerramento.",
                    "NENHUM APK FOI INSTALADO.", Amber);
            }
            else if (code == "APP_DOWNLOAD_NOT_CLOSED")
                ShowBlocked(1, 1, "Download ainda ativo",
                    "Conclua ou cancele o download no telefone.",
                    "NENHUM APK FOI INSTALADO.", Amber);
            else if (code == "N64_CORE_NOT_CLOSED")
                ShowBlocked(1, 1, "Motor N64 ainda ativo",
                    "O motor permaneceu aberto mesmo após a tentativa de encerramento seguro.",
                    "NENHUM APK FOI INSTALADO.", Amber);
            else if (code == "APP_SERVICE_NOT_CLOSED")
            {
                bool unavailable = receipt != null && receipt.appServiceCheck == "APP_SERVICES_CHECK_UNAVAILABLE";
                ShowBlocked(1, 1, unavailable ? "Checagem USB indisponível" : "Serviço do app ainda ativo",
                    unavailable ? "Não foi possível conferir os serviços. Reconecte o USB e tente novamente." :
                        "Encerre a atividade do TurboStations e tente novamente.",
                    "NENHUM APK FOI INSTALADO.", Amber);
            }
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
            var signal = ReadResultSignal(result.Output);
            if (signal != null && signal.Code == "ALREADY_INSTALLED" && signal.HashVerified)
            {
                completedStages = 4;
                activeStage = -1;
                blockedStage = -1;
                stage.Text = "VERSÃO JÁ INSTALADA";
                status.Text = "Telefone atualizado";
                statusDetail.Text = "O APK no telefone é idêntico ao pacote. Nenhuma transferência foi necessária.";
                progressCaption.Text = "Verificação concluída · " + elapsed.Elapsed.ToString(@"mm\:ss");
                progress.ShowMeasured(100, Green);
                SetActionHint("Abra o TurboStations para testar a versão instalada.", Green);
                UpdateStepLabels();
                retryAvailable = false;
                idleConfirmed.Checked = false;
                AppendLog("Versão já instalada; SHA-256 confirmado no telefone.");
                return;
            }
            if (signal != null && signal.Installed && signal.HashVerified &&
                result.ExitCode != 0)
            {
                completedStages = 4;
                activeStage = -1;
                blockedStage = -1;
                stage.Text = "INSTALAÇÃO CONFIRMADA";
                status.Text = "APK instalado e conferido";
                statusDetail.Text = signal.ReceiptSaved ?
                    "O telefone confirmou o SHA-256. Consulte o detalhe da ressalva." :
                    "O telefone confirmou o SHA-256; o recibo local não foi salvo.";
                progressCaption.Text = "Verificação concluída · " + elapsed.Elapsed.ToString(@"mm\:ss");
                progress.ShowMeasured(100, Green);
                SetActionHint("Não repita a instalação; confira a versão no telefone.", Amber);
                UpdateStepLabels();
                retryAvailable = false;
                idleConfirmed.Checked = false;
                AppendLog("Instalação e hash confirmados; " +
                    (signal.ReceiptSaved ? "resultado com ressalva." : "recibo local não foi salvo."));
                return;
            }
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
                bool verifiedWithoutReceipt = receipt == null &&
                    (result.Output ?? "").IndexOf("instalação e SHA256 conferidos.",
                        StringComparison.OrdinalIgnoreCase) >= 0;
                if (verifiedWithoutReceipt)
                {
                    completedStages = 4;
                    activeStage = -1;
                    blockedStage = -1;
                    stage.Text = "INSTALAÇÃO CONFIRMADA";
                    status.Text = "APK instalado e conferido";
                    statusDetail.Text = "O telefone confirmou o SHA-256, mas o recibo local não foi salvo.";
                    progressCaption.Text = "Verificação concluída · " + elapsed.Elapsed.ToString(@"mm\:ss");
                    progress.ShowMeasured(100, Green);
                    SetActionHint("Não repita a instalação; confira a versão no telefone.", Amber);
                    UpdateStepLabels();
                    retryAvailable = false;
                    idleConfirmed.Checked = false;
                    AppendLog("Instalação e hash confirmados, porém o recibo local não foi salvo.");
                    return;
                }
                string code = signal != null ? signal.Code :
                    (receipt == null ? "" : receipt.resultCode ?? "");
                bool uncertain = (receipt == null && completedStages >= 2) ||
                    code == "INSTALL_STATUS_UNKNOWN_TIMEOUT" ||
                    code == "INSTALL_STATUS_UNKNOWN_LOCAL_ERROR" ||
                    code == "INSTALL_NOT_CONFIRMED" ||
                    code == "USB_DISCONNECTED" ||
                    code == "USB_OFFLINE" ||
                    code == "USB_UNAUTHORIZED" ||
                    (result.Output ?? "").IndexOf("INSTALL_STATUS_UNKNOWN_TIMEOUT", StringComparison.OrdinalIgnoreCase) >= 0;
                if (signal != null) uncertain = code == "INSTALL_STATUS_UNKNOWN_TIMEOUT" ||
                    code == "INSTALL_STATUS_UNKNOWN_LOCAL_ERROR" ||
                    code == "INSTALL_NOT_CONFIRMED" ||
                    code == "USB_DISCONNECTED" ||
                    code == "USB_OFFLINE" ||
                    code == "USB_UNAUTHORIZED";
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
                else ShowInstallFailure(code, signal != null ? signal.Installed :
                    (receipt == null ? completedStages >= 2 : receipt.installAttempted),
                    receipt);
                if (!String.IsNullOrWhiteSpace(result.Error)) AppendLog(result.Error.Trim());
                retryAvailable = !uncertain &&
                    !(signal != null && signal.Installed) &&
                    !(receipt != null && receipt.installSuccess);
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
        if (!File.Exists(script) || (validateOnly && !File.Exists(manifest)))
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
