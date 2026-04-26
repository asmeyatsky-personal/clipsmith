// Phase 6.1 — lightweight in-app i18n.
// Static JSON message bundles loaded eagerly. Bundles stay small (~30
// strings) because the static export ships everything to the device. Add
// new keys here, keep all locales in sync, and use t("key") in components.

export const LOCALES = ["en", "es", "pt", "fr", "de", "ja", "ko"] as const;
export type Locale = (typeof LOCALES)[number];

export const LOCALE_LABELS: Record<Locale, string> = {
  en: "English",
  es: "Español",
  pt: "Português",
  fr: "Français",
  de: "Deutsch",
  ja: "日本語",
  ko: "한국어",
};

export type MessageKey =
  | "nav.feed" | "nav.discover" | "nav.record" | "nav.profile" | "nav.community"
  | "auth.login" | "auth.logout" | "auth.register" | "auth.email" | "auth.password"
  | "feed.empty" | "feed.loading" | "feed.error"
  | "video.like" | "video.comment" | "video.share" | "video.subscribe" | "video.locked"
  | "common.save" | "common.cancel" | "common.delete" | "common.loading" | "common.error" | "common.retry"
  | "settings.language";

type MessageBundle = Record<MessageKey, string>;

const en: MessageBundle = {
  "nav.feed": "Feed",
  "nav.discover": "Discover",
  "nav.record": "Record",
  "nav.profile": "Profile",
  "nav.community": "Community",
  "auth.login": "Log in",
  "auth.logout": "Log out",
  "auth.register": "Sign up",
  "auth.email": "Email",
  "auth.password": "Password",
  "feed.empty": "Your feed is empty.",
  "feed.loading": "Loading feed…",
  "feed.error": "Could not load feed.",
  "video.like": "Like",
  "video.comment": "Comment",
  "video.share": "Share",
  "video.subscribe": "Subscribe",
  "video.locked": "Subscribers only",
  "common.save": "Save",
  "common.cancel": "Cancel",
  "common.delete": "Delete",
  "common.loading": "Loading…",
  "common.error": "Something went wrong",
  "common.retry": "Try again",
  "settings.language": "Language",
};

const es: MessageBundle = {
  "nav.feed": "Inicio", "nav.discover": "Descubrir", "nav.record": "Grabar", "nav.profile": "Perfil", "nav.community": "Comunidad",
  "auth.login": "Iniciar sesión", "auth.logout": "Cerrar sesión", "auth.register": "Registrarse", "auth.email": "Correo electrónico", "auth.password": "Contraseña",
  "feed.empty": "Tu feed está vacío.", "feed.loading": "Cargando feed…", "feed.error": "No se pudo cargar el feed.",
  "video.like": "Me gusta", "video.comment": "Comentar", "video.share": "Compartir", "video.subscribe": "Suscribirse", "video.locked": "Solo suscriptores",
  "common.save": "Guardar", "common.cancel": "Cancelar", "common.delete": "Eliminar", "common.loading": "Cargando…", "common.error": "Algo salió mal", "common.retry": "Reintentar",
  "settings.language": "Idioma",
};

const pt: MessageBundle = {
  "nav.feed": "Início", "nav.discover": "Descobrir", "nav.record": "Gravar", "nav.profile": "Perfil", "nav.community": "Comunidade",
  "auth.login": "Entrar", "auth.logout": "Sair", "auth.register": "Cadastrar", "auth.email": "E-mail", "auth.password": "Senha",
  "feed.empty": "Seu feed está vazio.", "feed.loading": "Carregando feed…", "feed.error": "Não foi possível carregar o feed.",
  "video.like": "Curtir", "video.comment": "Comentar", "video.share": "Compartilhar", "video.subscribe": "Assinar", "video.locked": "Somente assinantes",
  "common.save": "Salvar", "common.cancel": "Cancelar", "common.delete": "Excluir", "common.loading": "Carregando…", "common.error": "Algo deu errado", "common.retry": "Tentar novamente",
  "settings.language": "Idioma",
};

const fr: MessageBundle = {
  "nav.feed": "Fil", "nav.discover": "Découvrir", "nav.record": "Enregistrer", "nav.profile": "Profil", "nav.community": "Communauté",
  "auth.login": "Se connecter", "auth.logout": "Se déconnecter", "auth.register": "S'inscrire", "auth.email": "E-mail", "auth.password": "Mot de passe",
  "feed.empty": "Votre fil est vide.", "feed.loading": "Chargement du fil…", "feed.error": "Impossible de charger le fil.",
  "video.like": "J'aime", "video.comment": "Commenter", "video.share": "Partager", "video.subscribe": "S'abonner", "video.locked": "Réservé aux abonnés",
  "common.save": "Enregistrer", "common.cancel": "Annuler", "common.delete": "Supprimer", "common.loading": "Chargement…", "common.error": "Une erreur s'est produite", "common.retry": "Réessayer",
  "settings.language": "Langue",
};

const de: MessageBundle = {
  "nav.feed": "Feed", "nav.discover": "Entdecken", "nav.record": "Aufnehmen", "nav.profile": "Profil", "nav.community": "Community",
  "auth.login": "Anmelden", "auth.logout": "Abmelden", "auth.register": "Registrieren", "auth.email": "E-Mail", "auth.password": "Passwort",
  "feed.empty": "Dein Feed ist leer.", "feed.loading": "Feed wird geladen…", "feed.error": "Feed konnte nicht geladen werden.",
  "video.like": "Gefällt mir", "video.comment": "Kommentieren", "video.share": "Teilen", "video.subscribe": "Abonnieren", "video.locked": "Nur für Abonnenten",
  "common.save": "Speichern", "common.cancel": "Abbrechen", "common.delete": "Löschen", "common.loading": "Lädt…", "common.error": "Etwas ist schief gelaufen", "common.retry": "Erneut versuchen",
  "settings.language": "Sprache",
};

const ja: MessageBundle = {
  "nav.feed": "フィード", "nav.discover": "発見", "nav.record": "録画", "nav.profile": "プロフィール", "nav.community": "コミュニティ",
  "auth.login": "ログイン", "auth.logout": "ログアウト", "auth.register": "登録", "auth.email": "メール", "auth.password": "パスワード",
  "feed.empty": "フィードは空です。", "feed.loading": "フィードを読み込み中…", "feed.error": "フィードを読み込めません。",
  "video.like": "いいね", "video.comment": "コメント", "video.share": "シェア", "video.subscribe": "登録する", "video.locked": "サブスクライバー限定",
  "common.save": "保存", "common.cancel": "キャンセル", "common.delete": "削除", "common.loading": "読み込み中…", "common.error": "問題が発生しました", "common.retry": "再試行",
  "settings.language": "言語",
};

const ko: MessageBundle = {
  "nav.feed": "피드", "nav.discover": "탐색", "nav.record": "녹화", "nav.profile": "프로필", "nav.community": "커뮤니티",
  "auth.login": "로그인", "auth.logout": "로그아웃", "auth.register": "가입", "auth.email": "이메일", "auth.password": "비밀번호",
  "feed.empty": "피드가 비어 있습니다.", "feed.loading": "피드 로드 중…", "feed.error": "피드를 불러올 수 없습니다.",
  "video.like": "좋아요", "video.comment": "댓글", "video.share": "공유", "video.subscribe": "구독", "video.locked": "구독자 전용",
  "common.save": "저장", "common.cancel": "취소", "common.delete": "삭제", "common.loading": "불러오는 중…", "common.error": "문제가 발생했습니다", "common.retry": "다시 시도",
  "settings.language": "언어",
};

export const MESSAGES: Record<Locale, MessageBundle> = { en, es, pt, fr, de, ja, ko };
