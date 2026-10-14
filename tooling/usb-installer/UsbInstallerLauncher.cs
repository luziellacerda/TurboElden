using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
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

    private sealed class InstallerForm : Form
    {
        private readonly string folder;
        private readonly string script;
        private readonly string manifestFile;
        private readonly Label title = new Label();
        private readonly Label warning = new Label();
        private readonly Label status = new Label();
        private readonly ListBox phones = new ListBox();
        private readonly CheckBox idleConfirmed = new CheckBox();
        private readonly Button refresh = new Button();
        private readonly Button install = new Button();
        private readonly Button retry = new Button();
        private readonly Button verify = new Button();
        private readonly Button close = new Button();
        private readonly ProgressBar progress = new ProgressBar();
        private readonly TextBox log = new TextBox();
        private readonly LinkLabel receipts = new LinkLabel();
        private readonly List<string> knownSerials = new List<string>();
        private bool manifestValid;
        private bool busy;
        private bool retryAvailable;
        private bool measuredProgress;
        private string currentKind;

        public InstallerForm(string baseFolder, string scriptPath, string manifestPath)
        {
            folder = baseFolder;
            script = scriptPath;
            manifestFile = manifestPath;
            Text = "TurboStations — instalação por USB";
            Font = new Font("Segoe UI", 9F);
            AutoScaleMode = AutoScaleMode.Dpi;
            BackColor = Color.FromArgb(242, 247, 252);
            StartPosition = FormStartPosition.CenterScreen;
            FormBorderStyle = FormBorderStyle.Sizable;
            MinimumSize = new Size(800, 690);
            ClientSize = new Size(780, 650);

            title.SetBounds(24, 18, 732, 38);
            title.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            title.ForeColor = Color.FromArgb(20, 46, 83);
            title.Font = new Font("Segoe UI", 16F, FontStyle.Bold);
            warning.SetBounds(24, 58, 732, 75);
            warning.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            warning.ForeColor = Color.FromArgb(112, 64, 0);
            warning.TextAlign = ContentAlignment.MiddleLeft;

            var devicesLabel = new Label();
            devicesLabel.Text = "1  Escolha o telefone conectado por USB";
            devicesLabel.SetBounds(24, 146, 490, 26);
            devicesLabel.TextAlign = ContentAlignment.MiddleLeft;
            refresh.Text = "Atualizar telefones";
            refresh.SetBounds(555, 142, 201, 34);
            refresh.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            refresh.Click += delegate { StartRefresh(); };
            phones.SetBounds(24, 184, 732, 154);
            phones.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            phones.IntegralHeight = false;
            phones.SelectionMode = SelectionMode.One;
            phones.SelectedIndexChanged += delegate {
                retryAvailable = false;
                idleConfirmed.Checked = false;
                UpdateButtons();
            };

            idleConfirmed.SetBounds(24, 350, 732, 47);
            idleConfirmed.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            idleConfirmed.Text = "Saí da partida, concluí os downloads e deixei a tela inicial do TurboStations ou do Android aberta.";
            idleConfirmed.CheckedChanged += delegate { UpdateButtons(); };
            install.Text = "Instalar no telefone selecionado";
            install.SetBounds(24, 411, 344, 42);
            install.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            install.BackColor = Color.FromArgb(24, 92, 183);
            install.ForeColor = Color.White;
            install.FlatStyle = FlatStyle.Flat;
            install.FlatAppearance.BorderSize = 0;
            install.Click += delegate { StartInstall(); };
            retry.Text = "Repetir";
            retry.SetBounds(380, 411, 138, 42);
            retry.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            retry.Click += delegate { StartInstall(); };
            verify.Text = "Verificar APK";
            verify.SetBounds(530, 411, 110, 42);
            verify.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            verify.Click += delegate { StartValidation(); };
            close.Text = "Fechar";
            close.SetBounds(652, 411, 104, 42);
            close.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            close.Click += delegate { Close(); };

            progress.SetBounds(24, 467, 732, 16);
            progress.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            progress.Style = ProgressBarStyle.Continuous;
            progress.MarqueeAnimationSpeed = 0;
            status.SetBounds(24, 490, 732, 29);
            status.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            status.TextAlign = ContentAlignment.MiddleLeft;
            log.SetBounds(24, 527, 732, 82);
            log.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            log.Multiline = true;
            log.ReadOnly = true;
            log.ScrollBars = ScrollBars.Vertical;
            log.BackColor = Color.White;
            receipts.SetBounds(24, 617, 360, 22);
            receipts.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            receipts.Text = "Abrir recibos das instalações";
            receipts.LinkClicked += delegate { OpenReceipts(); };

            Controls.AddRange(new Control[] {
                title, warning, devicesLabel, refresh, phones, idleConfirmed,
                install, retry, verify, close, progress, status, log, receipts
            });
            FormClosing += OnFormClosing;
            Shown += delegate { BeginInvoke(new Action(StartRefresh)); };
            LoadManifest();
            UpdateButtons();
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
                title.Text = "TurboStations " + manifest.revision + " — instalador USB";
                warning.Text = String.IsNullOrWhiteSpace(manifest.warning)
                    ? "Confira a revisão antes de atualizar o telefone." : manifest.warning;
                manifestValid = true;
                SetStatus("Conecte e desbloqueie o telefone. A busca USB começará automaticamente.");
            }
            catch (Exception error)
            {
                title.Text = "TurboStations — instalador USB";
                warning.Text = "O pacote de instalação está incompleto.";
                SetStatus("Confira o APK e o manifesto ao lado do instalador.");
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

        private void UpdatePhase(string line)
        {
            if (String.IsNullOrWhiteSpace(line)) return;
            if (line.IndexOf("Conferindo o APK", StringComparison.OrdinalIgnoreCase) >= 0)
                SetStatus(currentKind == "install" ? "1/4  Conferindo o APK..." : "Conferindo o APK...");
            if (line.IndexOf("Preparar Telefone", StringComparison.OrdinalIgnoreCase) >= 0)
                ShowIndeterminate("2/4  Conferindo USB, partida e downloads...");
            if (line.IndexOf("Preparar Telefone", StringComparison.OrdinalIgnoreCase) < 0 &&
                line.IndexOf("Preparar ", StringComparison.OrdinalIgnoreCase) >= 0)
                ShowIndeterminate("2/4  Conferindo USB, partida e downloads...");
            if (line.IndexOf("Instalando R", StringComparison.OrdinalIgnoreCase) >= 0)
                ShowIndeterminate("3/4  Transferindo e instalando. Mantenha o cabo conectado.");
            if (line.IndexOf("atualização instalada. Conferindo", StringComparison.OrdinalIgnoreCase) >= 0)
                ShowIndeterminate("4/4  Conferindo o APK instalado no telefone...");
        }

        private void ShowIndeterminate(string message)
        {
            measuredProgress = false;
            progress.Style = ProgressBarStyle.Marquee;
            progress.MarqueeAnimationSpeed = busy ? 24 : 0;
            SetStatus(message);
        }

        private bool ShowMeasuredProgress(string line)
        {
            const string marker = "TS_PROGRESS|hash|";
            if (line == null || !line.StartsWith(marker, StringComparison.Ordinal)) return false;
            int percentage;
            if (!Int32.TryParse(line.Substring(marker.Length), out percentage) ||
                percentage < 0 || percentage > 100) return true;
            measuredProgress = true;
            progress.MarqueeAnimationSpeed = 0;
            progress.Style = ProgressBarStyle.Continuous;
            progress.Value = percentage;
            SetStatus((currentKind == "install" ? "1/4  " : "") +
                "Conferindo o APK: " + percentage + "%");
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
            install.Enabled = ready && selected && idleConfirmed.Checked && !retryAvailable;
            retry.Enabled = ready && selected && idleConfirmed.Checked && retryAvailable;
            close.Enabled = !busy;
            receipts.Enabled = !busy && Directory.Exists(Path.Combine(folder, "recibos-usb"));
            progress.Style = busy && !measuredProgress ? ProgressBarStyle.Marquee : ProgressBarStyle.Continuous;
            progress.MarqueeAnimationSpeed = busy && !measuredProgress ? 24 : 0;
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
            SetStatus("Procurando telefones USB autorizados...");
            AppendLog("Atualizando a lista de telefones.");
            StartCommand(new CommandRequest { Kind = "list", Arguments = "-ListUsbDevices" });
        }

        private void StartValidation()
        {
            if (busy) return;
            LoadManifest();
            if (!manifestValid) { UpdateButtons(); return; }
            SetStatus("Conferindo o arquivo completo. Aguarde...");
            AppendLog("Verificando o APK indicado no manifesto.");
            StartCommand(new CommandRequest { Kind = "validate", Arguments = "-ValidateOnly -GuiProgress", StreamOutput = true });
        }

        private void StartInstall()
        {
            if (busy || !manifestValid || !idleConfirmed.Checked) return;
            var device = phones.SelectedItem as UsbDevice;
            if (device == null || String.IsNullOrWhiteSpace(device.Serial) ||
                !Regex.IsMatch(device.Serial, "^[A-Za-z0-9._-]{1,128}$"))
            {
                SetStatus("Identificação USB inválida. Atualize a lista e tente novamente.");
                return;
            }
            retryAvailable = false;
            SetStatus("Conferindo e instalando. Mantenha o cabo conectado; pode levar vários minutos.");
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
            measuredProgress = false;
            progress.Value = 0;
            busy = true;
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
                AppendLog(line);
                UpdatePhase(line);
            };
            worker.RunWorkerCompleted += delegate(object sender, RunWorkerCompletedEventArgs e)
            {
                busy = false;
                if (e.Error != null)
                {
                    measuredProgress = true;
                    progress.Value = 0;
                    AppendLog("A operação não pôde ser concluída: " + e.Error.Message);
                    SetStatus("Falha. Confira os arquivos e tente novamente.");
                    retryAvailable = request.Kind == "install";
                    if (retryAvailable) idleConfirmed.Checked = false;
                    UpdateButtons();
                    return;
                }
                var result = (CommandResult)e.Result;
                measuredProgress = true;
                progress.Value = result.ExitCode == 0 ? 100 : 0;
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
                SetStatus("Não foi possível consultar os telefones. Confira o cabo e a depuração USB.");
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
                    SetStatus("Nenhum telefone USB autorizado. Desbloqueie e aceite a depuração.");
                else
                    SetStatus(phones.Items.Count + " telefone(s) USB autorizado(s). Selecione um para instalar.");
                if (listing.UnauthorizedCount > 0)
                    AppendLog(listing.UnauthorizedCount + " telefone(s) aguardam autorização de depuração USB.");
                if (listing.OfflineCount > 0)
                    AppendLog(listing.OfflineCount + " telefone(s) estão offline; reconecte o cabo.");
                if (listing.ExcludedCount > 0)
                    AppendLog("Conexões de rede, emuladores ou USB não confirmado foram ignorados.");
            }
            catch (Exception)
            {
                SetStatus("A resposta USB não pôde ser lida. Atualize novamente.");
                AppendLog("A consulta USB retornou dados inesperados.");
            }
        }

        private void FinishValidation(CommandResult result)
        {
            if (result.ExitCode == 0)
            {
                SetStatus("APK conferido. Escolha o telefone e confirme que está livre.");
                AppendLog("Arquivo, tamanho e SHA256 conferidos. Nenhum telefone foi alterado.");
            }
            else
            {
                SetStatus("APK não conferido. Confira o motivo no registro abaixo.");
                if (!String.IsNullOrWhiteSpace(result.Error)) AppendLog(result.Error.Trim());
            }
        }

        private void FinishInstall(CommandResult result)
        {
            if (result.ExitCode == 0)
            {
                SetStatus("Instalação concluída. Abra o TurboStations para testar.");
                AppendLog("Instalação concluída. Consulte o recibo indicado acima.");
                idleConfirmed.Checked = false;
                retryAvailable = false;
            }
            else
            {
                bool uncertain = (result.Output ?? "").IndexOf("INSTALL_STATUS_UNKNOWN_TIMEOUT",
                    StringComparison.OrdinalIgnoreCase) >= 0;
                SetStatus(uncertain
                    ? "USB sem resposta. Confira no telefone se instalou antes de tentar novamente."
                    : "Instalação não concluída. Corrija o motivo mostrado e clique em Repetir.");
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
        start.EnvironmentVariables["TS_USB_INSTALLER_UTF8"] = "1";
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
