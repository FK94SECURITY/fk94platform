/**
 * FK94 Security Checklist - OPSEC + Privacy
 * Bilingual: English and Spanish
 */

export type Priority = 'essential' | 'recommended' | 'advanced';
export type Language = 'en' | 'es';

export interface ChecklistItem {
  id: string;
  title: { en: string; es: string };
  description: { en: string; es: string };
  priority: Priority;
  tip?: { en: string; es: string }; // Mini explicación propia en lugar de link
  link?: string;
}

export interface ChecklistCategory {
  id: string;
  name: { en: string; es: string };
  icon: string;
  description: { en: string; es: string };
  items: ChecklistItem[];
}

export const checklistData: ChecklistCategory[] = [
  // ============================================
  // 1. PASSWORDS & AUTHENTICATION
  // ============================================
  {
    id: 'authentication',
    name: { en: 'Passwords & Auth', es: 'Contraseñas y Auth' },
    icon: '🔐',
    description: {
      en: 'Secure your accounts and credentials',
      es: 'Asegurá tus cuentas y credenciales'
    },
    items: [
      {
        id: 'auth-1',
        title: { en: 'Use a password manager', es: 'Usá un gestor de contraseñas' },
        description: {
          en: 'Bitwarden, 1Password, or KeePass. Never reuse passwords.',
          es: 'Bitwarden, 1Password o KeePass. Nunca reutilices contraseñas.'
        },
        priority: 'essential',
        tip: {
          en: 'Bitwarden is free and open source - our top pick',
          es: 'Bitwarden es gratis y open source - nuestra recomendación'
        },
      },
      {
        id: 'auth-2',
        title: { en: 'Enable 2FA everywhere', es: 'Activá 2FA en todos lados' },
        description: {
          en: 'Use authenticator apps (Aegis, Authy), not SMS.',
          es: 'Usá apps de autenticación (Aegis, Authy), no SMS.'
        },
        priority: 'essential',
        tip: {
          en: 'SMS can be intercepted via SIM swapping',
          es: 'Los SMS pueden ser interceptados via SIM swapping'
        },
      },
      {
        id: 'auth-3',
        title: { en: 'Use hardware keys for critical accounts', es: 'Usá llaves de hardware para cuentas críticas' },
        description: {
          en: 'YubiKey for email, banking, and crypto.',
          es: 'YubiKey para email, banco y crypto.'
        },
        priority: 'advanced',
        tip: {
          en: 'Physical keys are phishing-proof',
          es: 'Las llaves físicas son inmunes al phishing'
        },
      },
      {
        id: 'auth-4',
        title: { en: 'Check for breached passwords', es: 'Verificá passwords filtrados' },
        description: {
          en: "Verify your passwords aren't in known leaks.",
          es: 'Verificá que tus contraseñas no estén en filtraciones conocidas.'
        },
        priority: 'essential',
        tip: {
          en: 'Our scan checks this automatically',
          es: 'Nuestro escaneo verifica esto automáticamente'
        },
      },
      {
        id: 'auth-5',
        title: { en: 'Use email aliases for signups', es: 'Usá alias de email para registros' },
        description: {
          en: 'SimpleLogin or AnonAddy to compartmentalize identity.',
          es: 'SimpleLogin o AnonAddy para compartimentar tu identidad.'
        },
        priority: 'recommended',
        tip: {
          en: 'If one alias leaks, your real email stays private',
          es: 'Si un alias se filtra, tu email real sigue privado'
        },
      },
      {
        id: 'auth-6',
        title: { en: 'Secure backup codes offline', es: 'Guardá códigos de backup offline' },
        description: {
          en: 'Store 2FA recovery codes in a safe, not digitally.',
          es: 'Guardá códigos de recuperación 2FA en una caja fuerte, no digital.'
        },
        priority: 'essential',
        tip: {
          en: 'Print them and store in a fireproof safe',
          es: 'Imprimilos y guardalos en una caja fuerte ignífuga'
        },
      },
    ],
  },

  // ============================================
  // 2. NETWORK & VPN
  // ============================================
  {
    id: 'network',
    name: { en: 'Network & VPN', es: 'Red y VPN' },
    icon: '🌐',
    description: {
      en: 'Protect your internet connection',
      es: 'Protegé tu conexión a internet'
    },
    items: [
      {
        id: 'net-1',
        title: { en: 'Use a no-logs VPN', es: 'Usá una VPN sin logs' },
        description: {
          en: 'Mullvad, ProtonVPN, or IVPN. Pay with crypto for anonymity.',
          es: 'Mullvad, ProtonVPN o IVPN. Pagá con crypto para más anonimato.'
        },
        priority: 'essential',
        tip: {
          en: 'Mullvad accepts cash by mail - maximum privacy',
          es: 'Mullvad acepta efectivo por correo - máxima privacidad'
        },
      },
      {
        id: 'net-2',
        title: { en: 'Enable kill switch', es: 'Activá el kill switch' },
        description: {
          en: 'Prevent traffic leaks if VPN disconnects.',
          es: 'Evitá fugas de tráfico si la VPN se desconecta.'
        },
        priority: 'essential',
        tip: {
          en: 'Your real IP can leak for seconds without this',
          es: 'Tu IP real puede filtrarse por segundos sin esto'
        },
      },
      {
        id: 'net-3',
        title: { en: 'Use encrypted DNS (DoH/DoT)', es: 'Usá DNS encriptado (DoH/DoT)' },
        description: {
          en: 'Cloudflare 1.1.1.1 or Quad9 9.9.9.9.',
          es: 'Cloudflare 1.1.1.1 o Quad9 9.9.9.9.'
        },
        priority: 'essential',
        tip: {
          en: 'Your ISP can see every site you visit without this',
          es: 'Tu ISP puede ver cada sitio que visitás sin esto'
        },
      },
      {
        id: 'net-4',
        title: { en: 'Disable WebRTC in browser', es: 'Desactivá WebRTC en el navegador' },
        description: {
          en: 'Prevents IP leaks even with VPN enabled.',
          es: 'Evita fugas de IP incluso con VPN activada.'
        },
        priority: 'recommended',
        tip: {
          en: 'WebRTC can reveal your real IP to websites',
          es: 'WebRTC puede revelar tu IP real a los sitios'
        },
      },
      {
        id: 'net-5',
        title: { en: 'Use Tor for sensitive activities', es: 'Usá Tor para actividades sensibles' },
        description: {
          en: 'Maximum anonymity for research and sensitive tasks.',
          es: 'Máximo anonimato para investigación y tareas sensibles.'
        },
        priority: 'advanced',
        tip: {
          en: 'Triple encryption through 3 random nodes',
          es: 'Triple encriptación a través de 3 nodos aleatorios'
        },
      },
      {
        id: 'net-6',
        title: { en: 'Secure your home router', es: 'Asegurá tu router de casa' },
        description: {
          en: 'Change default password, disable WPS, update firmware.',
          es: 'Cambiá la contraseña por defecto, desactivá WPS, actualizá firmware.'
        },
        priority: 'essential',
        tip: {
          en: 'Default router passwords are public knowledge',
          es: 'Las contraseñas por defecto del router son públicas'
        },
      },
      {
        id: 'net-7',
        title: { en: 'Never use public Wi-Fi without VPN', es: 'Nunca uses Wi-Fi público sin VPN' },
        description: {
          en: 'Assume all public networks are compromised.',
          es: 'Asumí que todas las redes públicas están comprometidas.'
        },
        priority: 'essential',
        tip: {
          en: 'Attackers can intercept all your traffic on public networks',
          es: 'Atacantes pueden interceptar todo tu tráfico en redes públicas'
        },
      },
    ],
  },

  // ============================================
  // 3. DEVICE ENCRYPTION
  // ============================================
  {
    id: 'encryption',
    name: { en: 'Encryption', es: 'Encriptación' },
    icon: '🔒',
    description: {
      en: 'Encrypt your data at rest and in transit',
      es: 'Encriptá tus datos en reposo y en tránsito'
    },
    items: [
      {
        id: 'enc-1',
        title: { en: 'Enable full disk encryption', es: 'Activá encriptación de disco completo' },
        description: {
          en: 'BitLocker (Windows), FileVault (Mac), LUKS (Linux).',
          es: 'BitLocker (Windows), FileVault (Mac), LUKS (Linux).'
        },
        priority: 'essential',
        tip: {
          en: 'If your laptop is stolen, your data stays protected',
          es: 'Si roban tu laptop, tus datos quedan protegidos'
        },
      },
      {
        id: 'enc-2',
        title: { en: 'Encrypt your phone', es: 'Encriptá tu teléfono' },
        description: {
          en: 'Enable device encryption in settings (default on modern phones).',
          es: 'Activá encriptación del dispositivo en ajustes (por defecto en phones modernos).'
        },
        priority: 'essential',
        tip: {
          en: 'iPhones are encrypted by default, Android needs enabling',
          es: 'iPhones están encriptados por defecto, Android necesita activarlo'
        },
      },
      {
        id: 'enc-3',
        title: { en: 'Use encrypted cloud storage', es: 'Usá almacenamiento cloud encriptado' },
        description: {
          en: 'Cryptomator, Tresorit, or self-hosted solutions.',
          es: 'Cryptomator, Tresorit, o soluciones self-hosted.'
        },
        priority: 'recommended',
        tip: {
          en: 'Google/Dropbox can see your files - encryption fixes this',
          es: 'Google/Dropbox pueden ver tus archivos - la encriptación arregla esto'
        },
      },
      {
        id: 'enc-4',
        title: { en: 'Encrypt backups', es: 'Encriptá los backups' },
        description: {
          en: 'Never store unencrypted backups, especially in cloud.',
          es: 'Nunca guardes backups sin encriptar, especialmente en la nube.'
        },
        priority: 'essential',
        tip: {
          en: 'Backups often contain your most sensitive data',
          es: 'Los backups suelen contener tus datos más sensibles'
        },
      },
      {
        id: 'enc-5',
        title: { en: 'Use VeraCrypt for sensitive files', es: 'Usá VeraCrypt para archivos sensibles' },
        description: {
          en: 'Create encrypted containers for critical documents.',
          es: 'Creá contenedores encriptados para documentos críticos.'
        },
        priority: 'advanced',
        tip: {
          en: 'Hidden volumes provide plausible deniability',
          es: 'Los volúmenes ocultos dan negación plausible'
        },
      },
      {
        id: 'enc-6',
        title: { en: 'Set a strong BIOS/UEFI password', es: 'Poné un password fuerte de BIOS/UEFI' },
        description: {
          en: 'Prevent unauthorized boot modifications.',
          es: 'Evitá modificaciones de booteo no autorizadas.'
        },
        priority: 'advanced',
        tip: {
          en: 'Prevents evil maid attacks on your computer',
          es: 'Previene ataques "evil maid" en tu computadora'
        },
      },
    ],
  },

  // ============================================
  // 4. SECURE COMMUNICATIONS
  // ============================================
  {
    id: 'communications',
    name: { en: 'Communications', es: 'Comunicaciones' },
    icon: '💬',
    description: {
      en: 'Private and secure messaging',
      es: 'Mensajería privada y segura'
    },
    items: [
      {
        id: 'comm-1',
        title: { en: 'Use Signal for messaging', es: 'Usá Signal para mensajes' },
        description: {
          en: 'End-to-end encrypted, open source, minimal metadata.',
          es: 'Encriptado de punta a punta, open source, mínimos metadatos.'
        },
        priority: 'essential',
        tip: {
          en: 'Used by security researchers and journalists worldwide',
          es: 'Usado por investigadores de seguridad y periodistas en todo el mundo'
        },
      },
      {
        id: 'comm-2',
        title: { en: 'Use ProtonMail for email', es: 'Usá ProtonMail para email' },
        description: {
          en: 'Encrypted email based in Switzerland.',
          es: 'Email encriptado basado en Suiza.'
        },
        priority: 'recommended',
        tip: {
          en: 'Swiss privacy laws are among the strongest in the world',
          es: 'Las leyes de privacidad suizas son de las más fuertes del mundo'
        },
      },
      {
        id: 'comm-3',
        title: { en: 'Enable disappearing messages', es: 'Activá mensajes que desaparecen' },
        description: {
          en: 'Auto-delete sensitive conversations.',
          es: 'Auto-borrá conversaciones sensibles.'
        },
        priority: 'recommended',
        tip: {
          en: 'Even if your phone is seized, old messages are gone',
          es: 'Aunque incauten tu teléfono, los mensajes viejos ya no están'
        },
      },
      {
        id: 'comm-4',
        title: { en: 'Verify contact keys', es: 'Verificá claves de contactos' },
        description: {
          en: 'Compare safety numbers in person when possible.',
          es: 'Compará números de seguridad en persona cuando sea posible.'
        },
        priority: 'advanced',
        tip: {
          en: 'Prevents man-in-the-middle attacks on your chats',
          es: 'Previene ataques man-in-the-middle en tus chats'
        },
      },
      {
        id: 'comm-5',
        title: { en: 'Disable message previews', es: 'Desactivá previews de mensajes' },
        description: {
          en: 'Hide content in lock screen notifications.',
          es: 'Ocultá contenido en notificaciones de pantalla bloqueada.'
        },
        priority: 'essential',
        tip: {
          en: 'Anyone looking at your phone sees your messages otherwise',
          es: 'Cualquiera que mire tu teléfono ve tus mensajes si no'
        },
      },
      {
        id: 'comm-6',
        title: { en: 'Use PGP for sensitive emails', es: 'Usá PGP para emails sensibles' },
        description: {
          en: 'GPG encryption for truly private correspondence.',
          es: 'Encriptación GPG para correspondencia realmente privada.'
        },
        priority: 'advanced',
        tip: {
          en: 'Battle-tested encryption since 1991',
          es: 'Encriptación probada en batalla desde 1991'
        },
      },
      {
        id: 'comm-7',
        title: { en: 'Never share sensitive info over SMS', es: 'Nunca compartas info sensible por SMS' },
        description: {
          en: 'SMS is unencrypted and easily intercepted.',
          es: 'SMS no está encriptado y es fácil de interceptar.'
        },
        priority: 'essential',
        tip: {
          en: 'SMS travels in plain text through cell towers',
          es: 'SMS viaja en texto plano a través de antenas celulares'
        },
      },
    ],
  },

  // ============================================
  // 5. BROWSER OPSEC
  // ============================================
  {
    id: 'browser',
    name: { en: 'Browser OPSEC', es: 'OPSEC de Navegador' },
    icon: '🖥️',
    description: {
      en: 'Prevent tracking and fingerprinting',
      es: 'Evitá tracking y fingerprinting'
    },
    items: [
      {
        id: 'browser-1',
        title: { en: 'Use a privacy browser', es: 'Usá un navegador de privacidad' },
        description: {
          en: 'Firefox with hardening, Brave, or LibreWolf.',
          es: 'Firefox con hardening, Brave, o LibreWolf.'
        },
        priority: 'essential',
        tip: {
          en: 'Chrome sends data to Google - Firefox does not',
          es: 'Chrome envía datos a Google - Firefox no'
        },
      },
      {
        id: 'browser-2',
        title: { en: 'Install uBlock Origin', es: 'Instalá uBlock Origin' },
        description: {
          en: 'Block ads, trackers, and malware.',
          es: 'Bloqueá ads, trackers y malware.'
        },
        priority: 'essential',
        tip: {
          en: 'Also speeds up page loading significantly',
          es: 'También acelera la carga de páginas significativamente'
        },
      },
      {
        id: 'browser-3',
        title: { en: 'Use a private search engine', es: 'Usá un buscador privado' },
        description: {
          en: 'DuckDuckGo, Startpage, or Brave Search.',
          es: 'DuckDuckGo, Startpage, o Brave Search.'
        },
        priority: 'essential',
        tip: {
          en: 'Google builds a profile of you from your searches',
          es: 'Google construye un perfil tuyo con tus búsquedas'
        },
      },
      {
        id: 'browser-4',
        title: { en: 'Block third-party cookies', es: 'Bloqueá cookies de terceros' },
        description: {
          en: 'Prevent cross-site tracking.',
          es: 'Evitá tracking entre sitios.'
        },
        priority: 'essential',
        tip: {
          en: 'Advertisers use these to follow you across the web',
          es: 'Los anunciantes usan esto para seguirte por la web'
        },
      },
      {
        id: 'browser-5',
        title: { en: 'Use container tabs', es: 'Usá pestañas contenedor' },
        description: {
          en: 'Firefox Multi-Account Containers to isolate activities.',
          es: 'Firefox Multi-Account Containers para aislar actividades.'
        },
        priority: 'recommended',
        tip: {
          en: 'Keep Facebook isolated from your banking',
          es: 'Mantené Facebook aislado de tu banco'
        },
      },
      {
        id: 'browser-6',
        title: { en: 'Minimize browser extensions', es: 'Minimizá las extensiones' },
        description: {
          en: 'Each extension increases fingerprint uniqueness.',
          es: 'Cada extensión aumenta la unicidad de tu fingerprint.'
        },
        priority: 'recommended',
        tip: {
          en: 'More extensions = easier to identify you',
          es: 'Más extensiones = más fácil identificarte'
        },
      },
      {
        id: 'browser-7',
        title: { en: 'Disable JavaScript on untrusted sites', es: 'Desactivá JavaScript en sitios no confiables' },
        description: {
          en: 'Use NoScript or uBlock for selective blocking.',
          es: 'Usá NoScript o uBlock para bloqueo selectivo.'
        },
        priority: 'advanced',
        tip: {
          en: 'Most browser exploits require JavaScript',
          es: 'La mayoría de exploits de navegador requieren JavaScript'
        },
      },
    ],
  },

  // ============================================
  // 6. IDENTITY COMPARTMENTALIZATION
  // ============================================
  {
    id: 'identity',
    name: { en: 'Identity OPSEC', es: 'OPSEC de Identidad' },
    icon: '🎭',
    description: {
      en: 'Separate and protect your identities',
      es: 'Separá y protegé tus identidades'
    },
    items: [
      {
        id: 'id-1',
        title: { en: 'Use separate emails for different purposes', es: 'Usá emails separados para distintos propósitos' },
        description: {
          en: 'Personal, work, finance, throwaway - never mix.',
          es: 'Personal, trabajo, finanzas, descartables - nunca mezcles.'
        },
        priority: 'essential',
        tip: {
          en: 'One breach stays contained to one identity',
          es: 'Una filtración queda contenida en una identidad'
        },
      },
      {
        id: 'id-2',
        title: { en: 'Use pseudonyms online', es: 'Usá seudónimos online' },
        description: {
          en: "Don't use real name unless necessary.",
          es: 'No uses tu nombre real a menos que sea necesario.'
        },
        priority: 'recommended',
        tip: {
          en: 'Your real name is permanent - pseudonyms are disposable',
          es: 'Tu nombre real es permanente - los seudónimos son descartables'
        },
      },
      {
        id: 'id-3',
        title: { en: 'Use different usernames per platform', es: 'Usá diferentes usernames por plataforma' },
        description: {
          en: 'Prevent cross-platform correlation.',
          es: 'Evitá correlación entre plataformas.'
        },
        priority: 'recommended',
        tip: {
          en: 'Same username everywhere = easy to track you',
          es: 'Mismo username en todos lados = fácil rastrearte'
        },
      },
      {
        id: 'id-4',
        title: { en: 'Get a VoIP number for signups', es: 'Conseguí un número VoIP para registros' },
        description: {
          en: "Don't give your real phone number to services.",
          es: 'No des tu número real a los servicios.'
        },
        priority: 'recommended',
        tip: {
          en: 'Your phone number is a unique identifier',
          es: 'Tu número de teléfono es un identificador único'
        },
      },
      {
        id: 'id-5',
        title: { en: 'Use virtual cards for purchases', es: 'Usá tarjetas virtuales para compras' },
        description: {
          en: 'Privacy.com or prepaid cards for anonymity.',
          es: 'Privacy.com o tarjetas prepagas para anonimato.'
        },
        priority: 'recommended',
        tip: {
          en: 'Your real card number stays protected from breaches',
          es: 'Tu número de tarjeta real queda protegido de filtraciones'
        },
      },
      {
        id: 'id-6',
        title: { en: 'Remove metadata from files', es: 'Eliminá metadatos de archivos' },
        description: {
          en: 'Strip EXIF data from photos before sharing.',
          es: 'Quitá datos EXIF de fotos antes de compartir.'
        },
        priority: 'recommended',
        tip: {
          en: 'Photos can contain your GPS location',
          es: 'Las fotos pueden contener tu ubicación GPS'
        },
      },
      {
        id: 'id-7',
        title: { en: 'Opt out of data brokers', es: 'Salí de los data brokers' },
        description: {
          en: 'Request removal from sites that publish your info.',
          es: 'Pedí que te saquen de sitios que publican tu info.'
        },
        priority: 'recommended',
        tip: {
          en: 'These sites sell your personal data to anyone',
          es: 'Estos sitios venden tus datos personales a cualquiera'
        },
      },
    ],
  },

  // ============================================
  // 7. MOBILE SECURITY
  // ============================================
  {
    id: 'mobile',
    name: { en: 'Mobile Security', es: 'Seguridad Móvil' },
    icon: '📱',
    description: {
      en: 'Secure your smartphone',
      es: 'Asegurá tu smartphone'
    },
    items: [
      {
        id: 'mobile-1',
        title: { en: 'Use a strong PIN (6+ digits)', es: 'Usá un PIN fuerte (6+ dígitos)' },
        description: {
          en: 'Avoid patterns and short PINs.',
          es: 'Evitá patrones y PINs cortos.'
        },
        priority: 'essential',
        tip: {
          en: '4-digit PIN = 10,000 combos. 6-digit = 1,000,000',
          es: 'PIN de 4 dígitos = 10,000 combos. 6 dígitos = 1,000,000'
        },
      },
      {
        id: 'mobile-2',
        title: { en: 'Review and revoke app permissions', es: 'Revisá y revocá permisos de apps' },
        description: {
          en: 'Remove unnecessary access to location, camera, mic.',
          es: 'Quitá acceso innecesario a ubicación, cámara, micrófono.'
        },
        priority: 'essential',
        tip: {
          en: 'Most apps request more permissions than they need',
          es: 'La mayoría de apps piden más permisos de los que necesitan'
        },
      },
      {
        id: 'mobile-3',
        title: { en: 'Disable location services', es: 'Desactivá servicios de ubicación' },
        description: {
          en: 'Only enable for apps that truly need it.',
          es: 'Solo activá para apps que realmente lo necesiten.'
        },
        priority: 'essential',
        tip: {
          en: 'Your location history reveals your entire life',
          es: 'Tu historial de ubicación revela toda tu vida'
        },
      },
      {
        id: 'mobile-4',
        title: { en: 'Enable SIM PIN', es: 'Activá PIN de SIM' },
        description: {
          en: 'Protect against SIM swapping attacks.',
          es: 'Protegé contra ataques de SIM swapping.'
        },
        priority: 'essential',
        tip: {
          en: 'Without this, thieves can receive your 2FA codes',
          es: 'Sin esto, ladrones pueden recibir tus códigos 2FA'
        },
      },
      {
        id: 'mobile-5',
        title: { en: 'Disable Bluetooth when not in use', es: 'Desactivá Bluetooth cuando no lo uses' },
        description: {
          en: 'Prevent tracking and attacks.',
          es: 'Evitá tracking y ataques.'
        },
        priority: 'recommended',
        tip: {
          en: 'Bluetooth can be used to track your movements',
          es: 'Bluetooth puede usarse para rastrear tus movimientos'
        },
      },
      {
        id: 'mobile-6',
        title: { en: 'Use GrapheneOS or CalyxOS', es: 'Usá GrapheneOS o CalyxOS' },
        description: {
          en: 'Privacy-focused Android alternatives.',
          es: 'Alternativas de Android enfocadas en privacidad.'
        },
        priority: 'advanced',
        tip: {
          en: 'Google-free Android with enhanced security',
          es: 'Android sin Google con seguridad mejorada'
        },
      },
      {
        id: 'mobile-7',
        title: { en: 'Disable ad tracking', es: 'Desactivá tracking de publicidad' },
        description: {
          en: 'Opt out in privacy settings.',
          es: 'Desactivá en ajustes de privacidad.'
        },
        priority: 'essential',
        tip: {
          en: 'Your advertising ID follows you across all apps',
          es: 'Tu ID de publicidad te sigue a través de todas las apps'
        },
      },
    ],
  },

  // ============================================
  // 8. CRYPTOCURRENCY OPSEC
  // ============================================
  {
    id: 'crypto',
    name: { en: 'Crypto OPSEC', es: 'OPSEC Crypto' },
    icon: '₿',
    description: {
      en: 'Protect your crypto assets',
      es: 'Protegé tus activos crypto'
    },
    items: [
      {
        id: 'crypto-1',
        title: { en: 'Use a hardware wallet', es: 'Usá una hardware wallet' },
        description: {
          en: 'Ledger or Trezor for significant holdings.',
          es: 'Ledger o Trezor para holdings significativos.'
        },
        priority: 'essential',
        tip: {
          en: 'Keys never leave the device - unhackable remotely',
          es: 'Las claves nunca salen del dispositivo - inhackeable remotamente'
        },
      },
      {
        id: 'crypto-2',
        title: { en: 'Store seed phrase offline', es: 'Guardá la seed phrase offline' },
        description: {
          en: 'Metal plate, never digital. Multiple secure locations.',
          es: 'Placa de metal, nunca digital. Múltiples ubicaciones seguras.'
        },
        priority: 'essential',
        tip: {
          en: 'Digital storage = hackable. Metal survives fire',
          es: 'Almacenamiento digital = hackeable. El metal sobrevive al fuego'
        },
      },
      {
        id: 'crypto-3',
        title: { en: 'Use separate wallets', es: 'Usá wallets separadas' },
        description: {
          en: 'Hot wallet (daily), cold wallet (savings).',
          es: 'Hot wallet (diario), cold wallet (ahorros).'
        },
        priority: 'recommended',
        tip: {
          en: 'Like carrying cash vs. keeping savings in a vault',
          es: 'Como llevar efectivo vs. guardar ahorros en una bóveda'
        },
      },
      {
        id: 'crypto-4',
        title: { en: 'Verify addresses character by character', es: 'Verificá direcciones caracter por caracter' },
        description: {
          en: 'Clipboard malware can swap addresses.',
          es: 'Malware de clipboard puede cambiar direcciones.'
        },
        priority: 'essential',
        tip: {
          en: 'Millions lost to clipboard hijacking attacks',
          es: 'Millones perdidos por ataques de secuestro de clipboard'
        },
      },
      {
        id: 'crypto-5',
        title: { en: 'Revoke unused token approvals', es: 'Revocá aprobaciones de tokens no usadas' },
        description: {
          en: 'Use revoke.cash to remove old permissions.',
          es: 'Usá revoke.cash para remover permisos viejos.'
        },
        priority: 'recommended',
        tip: {
          en: 'Old approvals can drain your wallet later',
          es: 'Aprobaciones viejas pueden vaciar tu wallet después'
        },
      },
      {
        id: 'crypto-6',
        title: { en: 'Never share holdings publicly', es: 'Nunca compartas holdings públicamente' },
        description: {
          en: 'Makes you a target for attacks.',
          es: 'Te convierte en objetivo de ataques.'
        },
        priority: 'essential',
        tip: {
          en: 'Wrench attacks target known wealthy holders',
          es: 'Ataques con "llave inglesa" apuntan a holders con plata conocida'
        },
      },
      {
        id: 'crypto-7',
        title: { en: 'Use a dedicated device for crypto', es: 'Usá un dispositivo dedicado para crypto' },
        description: {
          en: 'Separate machine for transactions.',
          es: 'Máquina separada para transacciones.'
        },
        priority: 'advanced',
        tip: {
          en: 'No malware risk from daily browsing',
          es: 'Sin riesgo de malware del uso diario del navegador'
        },
      },
    ],
  },
];

// Helper functions
export function getAllItems(): ChecklistItem[] {
  return checklistData.flatMap(category => category.items);
}

export function getItemsByPriority(priority: Priority): ChecklistItem[] {
  return getAllItems().filter(item => item.priority === priority);
}

export function getCategoryById(id: string): ChecklistCategory | undefined {
  return checklistData.find(category => category.id === id);
}

// Get localized text helper
export function getLocalizedText(obj: { en: string; es: string }, lang: Language): string {
  return obj[lang] || obj.en;
}

export const PRIORITY_CONFIG = {
  essential: {
    label: { en: 'Essential', es: 'Esencial' },
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    borderColor: 'border-red-500/30',
  },
  recommended: {
    label: { en: 'Recommended', es: 'Recomendado' },
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
  },
  advanced: {
    label: { en: 'Advanced', es: 'Avanzado' },
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
  },
};

export const STATS = {
  totalCategories: checklistData.length,
  totalItems: getAllItems().length,
  essentialItems: getItemsByPriority('essential').length,
  recommendedItems: getItemsByPriority('recommended').length,
  advancedItems: getItemsByPriority('advanced').length,
};
