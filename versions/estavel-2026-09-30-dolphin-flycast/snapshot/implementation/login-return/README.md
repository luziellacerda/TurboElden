# Retorno dos jogos preservando login

Causa no código: AuthSession tinha apenas boolean estático. ESActivity.onDestroy encerra o processo quando não há download; recriação ou pressão de memória também perde o boolean. ESActivity.onResume exige AuthSession, então a instância recriada redireciona para login.

Correção: AuthSession carrega sessão local previamente autenticada ao entrar no login ou no guard do frontend. Autenticação continua chamando a implementação original LocalPassword.matches, preservada integralmente. Registro AES-256-GCM em noBackupFilesDir, chave no Android Keystore; sem guardar senha, sem restauração por backup e sem acesso externo exportado. Registro inválido/ausente exige senha normalmente. Assinatura do APK e revisão do validador original delimitam a sessão.

Primeiro uso após atualizar ainda exige login uma vez para criar o registro. Depois sobrevive à recriação do processo e reabertura do app; apagar dados/reinstalar ou mudar o validador invalida a sessão. Licença do catálogo e regras do serviço não são modificadas.

Fonte nova em java/.../AuthSession.java.template; Java definitivo é gerado com a identificação do validador, nunca com a senha. Patch adiciona attach(Context) no onCreate e ensureAuthorized originais do login; demais métodos e classes preservados.

Montagem: build.py --base-apk CAMINHO --base-sha256 SHA256. Usar como etapa final depois de qualquer montagem visual para conservar a correção de sessão. Altera somente classes8.dex; motores, native, helpers de mídia e assets são copiados intactos. LoginActivity.java visual também recebeu attach, mas build_brand_login.py histórico não deve substituir a nova sessão.

Diagnóstico por leitura de código, sem logs recentes do aparelho (USB ausente). Compilar não equivale a confirmar o retorno no aparelho. APK estável anterior preservado e sem publicação automática.
