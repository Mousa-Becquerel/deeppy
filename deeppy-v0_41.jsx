import { useState, useRef, useEffect, useCallback } from "react";

// ─── Analytics Init (conditional on consent) ───
const initAnalytics = () => {
  if (typeof window === "undefined") return;
  // Google Analytics
  if (!window.__ga_loaded) {
    window.__ga_loaded = true;
    const s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=G-FZ2QYDF1Y6";
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function() { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", "G-FZ2QYDF1Y6");
  }
  // PostHog
  if (!window.__ph_loaded) {
    window.__ph_loaded = true;
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog&&window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture identify setPersonProperties group reset get_distinct_id get_session_id opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing startSessionRecording stopSessionRecording register register_once".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
    window.posthog.init("phc_mBMELW4dJmY7Ge19DIuy9HiMxoqUAdHVvFuGpDrfWQZ", {
      api_host: "https://eu.i.posthog.com",
      person_profiles: "identified_only",
      autocapture: true,
      capture_pageview: true,
      capture_pageleave: true,
    });
  }
};

// ─── Meta Tags ───
if (typeof window !== "undefined" && !window.__meta_set) {
  window.__meta_set = true;
  document.title = "DeePPy — Digital Product Passport per prodotti da costruzione";
  const metas = [
    ["description", "Tutte le informazioni tecniche dei tuoi prodotti da costruzione in un unico posto. Allineato a ESPR EU 2024/1781."],
    ["og:title", "DeePPy — Digital Product Passport"],
    ["og:description", "Il passaporto digitale dei tuoi prodotti da costruzione. Risparmi tempo, ti presenti in modo professionale, hai il pieno controllo."],
    ["og:type", "website"],
    ["og:url", "https://deeppy.eu"],
    ["og:image", "https://deeppy.eu/og-image.png"],
    ["og:locale", "it_IT"],
    ["og:locale:alternate", "en_US"],
    ["twitter:card", "summary_large_image"],
    ["twitter:title", "DeePPy — Digital Product Passport"],
    ["twitter:description", "Il passaporto digitale dei tuoi prodotti da costruzione."],
  ];
  metas.forEach(([name, content]) => {
    const tag = document.createElement("meta");
    if (name.startsWith("og:") || name.startsWith("twitter:")) { tag.setAttribute("property", name); } else { tag.setAttribute("name", name); }
    tag.setAttribute("content", content);
    document.head.appendChild(tag);
  });
}

// ─── GDPR Cookie Banner ───
function CookieBanner({ lang }) {
  const [visible, setVisible] = useState(false);
  const it = lang === "it";
  useEffect(() => {
    if (typeof window === "undefined") return;
    const consent = localStorage.getItem("deeppy_consent");
    if (consent === "accepted") { initAnalytics(); }
    else if (!consent) { setVisible(true); }
  }, []);
  const accept = () => { localStorage.setItem("deeppy_consent", "accepted"); setVisible(false); initAnalytics(); };
  const reject = () => { localStorage.setItem("deeppy_consent", "rejected"); setVisible(false); };
  if (!visible) return null;
  return (
    <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, zIndex: 9999, background: "#0F1729", borderTop: "1px solid #1A2744", padding: "16px 32px", display: "flex", alignItems: "center", justifyContent: "center", gap: 20, fontFamily: "'Inter',-apple-system,system-ui,sans-serif" }}>
      <p style={{ fontSize: 13, color: "#94A3B8", margin: 0, maxWidth: 600, lineHeight: 1.5 }}>
        {it ? "Questo sito utilizza cookie tecnici e di analisi per migliorare l'esperienza. I dati sono elaborati nell'UE (GDPR compliant)." : "This site uses technical and analytics cookies to improve your experience. Data is processed in the EU (GDPR compliant)."}{" "}
        <a href="https://www.levery.it/privacy" target="_blank" rel="noopener noreferrer" style={{ color: "#34D399", textDecoration: "none" }}>Privacy Policy</a>
      </p>
      <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
        <button onClick={reject} style={{ padding: "8px 20px", borderRadius: 6, border: "1px solid #243356", background: "transparent", color: "#94A3B8", fontSize: 12, fontWeight: 600, cursor: "pointer", fontFamily: "inherit" }}>{it ? "Rifiuta" : "Decline"}</button>
        <button onClick={accept} style={{ padding: "8px 20px", borderRadius: 6, border: "none", background: "#34D399", color: "#0F1729", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "inherit" }}>{it ? "Accetta" : "Accept"}</button>
      </div>
    </div>
  );
}


const T = {
  navy: "#0F1729", navyLight: "#1A2744", navyMid: "#243356",
  accent: "#34D399", accentSoft: "#D1FAE5", accentDark: "#059669",
  amber: "#F59E0B", amberSoft: "#FEF3C7",
  red: "#EF4444", redSoft: "#FEE2E2",
  text: "#F1F5F9", textMuted: "#94A3B8",
  textDark: "#1E293B", textSec: "#64748B",
  bg: "#FFFFFF", bgSoft: "#F8FAFC",
  border: "#E2E8F0", borderLight: "#F1F5F9",
};
const font = "'Inter',-apple-system,system-ui,sans-serif";

const I = ({ d, size = 16, color = T.textSec, style: s }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, ...s }}>
    {typeof d === "string" ? <path d={d} /> : d}
  </svg>
);
const ic = {
  upload: "M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12",
  bolt: "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
  shield: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
  globe: <><circle cx="12" cy="12" r="10" /><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" /></>,
  lock: <><rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0110 0v4" /></>,
  chart: "M18 20V10M12 20V4M6 20v-6",
  box: "M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16zM3.27 6.96L12 12.01l8.73-5.05M12 22.08V12",
  factory: "M2 20h20M4 20V8l4 3V8l4 3V4h8v16",
  tool: "M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z",
  compass: <><circle cx="12" cy="12" r="10" /><path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36z" /></>,
  file: "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8",
  check: "M20 6L9 17l-5-5",
  alert: <><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /><path d="M12 9v4M12 17h.01" /></>,
  x: "M18 6L6 18M6 6l12 12",
  trash: "M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6",
  search: <><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" /></>,
  download: "M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3",
  share: <><circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" /><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98" /></>,
  printer: "M6 9V2h12v7M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2M6 14h12v8H6z",
  edit: "M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4z",
  layers: "M12 2L2 7l10 5 10-5zM2 17l10 5 10-5M2 12l10 5 10-5",
  thermo: "M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z",
  droplet: "M12 2.69l5.66 5.66a8 8 0 11-11.31 0z",
  flame: "M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.07-2.14 0-5.5 3-7 .5 2.5 2 4.9 4 6.5 3 2.5 3 5.5 0 8.5a5 5 0 01-8.5-2.5z",
  settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" /></>,
  users: "M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75",
  leaf: "M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.67c.65.54 1.51.96 2.34 1.17C12.74 21.44 17 19.27 17 19.27S19 15.27 15 11.27c0 0-4-1-8 2",
  grid: <><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></>,
  home: "M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z",
  plus: "M12 5v14M5 12h14",
  arrow: "M5 12h14M12 5l7 7-7 7",
  msg: "M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z",
  clip: "M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2M9 2h6a1 1 0 011 1v1a1 1 0 01-1 1H9a1 1 0 01-1-1V3a1 1 0 011-1z",
  leaf2: "M11 20A7 7 0 019.8 6.9C15.5 5.5 20 4 20 4s-1.5 4.5-2.9 10.1A7 7 0 0111 20z",
  recycle: <><path d="M7 19H4.815a1.83 1.83 0 01-1.57-.881 1.785 1.785 0 01-.004-1.784L7.196 9.5" /><path d="M11 19h5.926a1.83 1.83 0 001.57-.881l2.245-3.887" /><path d="M13.5 6.5l2.5-4 2.5 4" /></>,
  energy: "M13 2L3 14h9l-1 8 10-12h-9l1-8z",
  pin: "M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0zM12 13a3 3 0 100-6 3 3 0 000 6z",
  clock: "M12 2a10 10 0 100 20 10 10 0 000-20zM12 6v6l4 2",
  chevDown: "M6 9l6 6 6-6",
  chevRight: "M9 18l6-6-6-6",
  chevLeft: "M15 18l-6-6 6-6",
  link: "M10 13a5 5 0 007.54.54l.01-.01a5 5 0 00-7.07-7.07l-1.72 1.71M14 11a5 5 0 00-7.54-.54l-.01.01a5 5 0 007.07 7.07l1.72-1.71",
  truck: "M1 3h15v13H1zM16 8h4l3 3v5h-7V8zM5.5 21a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM18.5 21a2.5 2.5 0 100-5 2.5 2.5 0 000 5z",
  window: <><rect x="3" y="3" width="18" height="18" rx="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="9" x2="9" y2="21" /></>,
  sliders: "M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6",
};

const LOGO_SRC = "data:image/png;base64,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";
const Logo = ({ dark, size = 22, withText = false }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
    <img src={LOGO_SRC} alt="DeePPy" style={{ height: size * 1.5, width: size * 1.5, objectFit: "cover", borderRadius: size * 0.35, display: "block" }} />
    {withText && <span style={{ fontSize: size * 0.82, fontWeight: 800, color: dark ? T.textDark : T.text, letterSpacing: "-0.02em", fontFamily: font }}>DeePPy</span>}
  </span>
);
const Btn = ({ children, primary, small, onClick, style: s }) => (
  <button onClick={onClick} style={{ padding: small ? "7px 16px" : "12px 24px", borderRadius: 8, border: primary ? "none" : `1px solid ${T.border}`, background: primary ? T.accent : T.bg, color: primary ? T.navy : T.textDark, fontSize: small ? 13 : 14, fontWeight: 700, cursor: "pointer", fontFamily: font, display: "inline-flex", alignItems: "center", gap: 6, transition: "all .15s", ...s }}>{children}</button>
);
const Badge = ({ children, color = T.accent, bg = T.accentSoft }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 4, padding: "3px 9px", borderRadius: 5, fontSize: 10, fontWeight: 700, letterSpacing: "0.04em", color, background: bg }}>{children}</span>
);
const Conf = ({ c, onClick }) => {
  const m = { high: [T.accent, T.accentSoft, ic.check, "Auto"], manual: [T.accent, T.accentSoft, ic.edit, "Manual"], medium: [T.amber, T.amberSoft, ic.alert, "Review"], low: [T.red, T.redSoft, ic.x, "Missing"] };
  const x = m[c] || m.low;
  return <span onClick={onClick} style={{ display: "inline-flex", alignItems: "center", gap: 3, padding: "2px 7px", borderRadius: 4, background: x[1], color: x[0], fontSize: 10, fontWeight: 700, cursor: onClick ? "pointer" : "default" }}><I d={x[2]} size={10} color={x[0]} />{x[3]}</span>;
};

// ─── TRANSLATION HELPER ─────────────────────────────────
const i18n = {
  // Sidebar
  passports: ["Passaporti", "Passports"], catalog: ["Catalogo", "Catalog"], newItem: ["Nuovo", "New"],
  documents: ["Documenti", "Documents"], settings: ["Impostazioni", "Settings"], admin: ["Amministrazione", "Administration"],
  // Tabs
  overview: ["Panoramica", "Overview"], composition: ["Composizione", "Composition"], performance: ["Prestazioni", "Performance"],
  compliance: ["Conformità", "Compliance"], lifecycle: ["Ciclo di Vita", "Lifecycle"],
  // Buttons
  assistant: ["Assistente", "Assistant"], saveDraft: ["Salva bozza", "Save draft"], saved: ["Salvato!", "Saved!"],
  preview: ["Anteprima", "Preview"], backTo: ["Torna ai Passaporti", "Back to Passports"], edit: ["Modifica", "Edit"],
  confirm: ["Conferma", "Confirm"], add: ["Aggiungi", "Add"], remove: ["Rimuovi", "Remove"], 
  invite: ["Invita", "Invite"], send: ["Invia", "Send"], unlink: ["Scollega", "Unlink"],
  // Status
  draft: ["Bozza", "Draft"], published: ["Pubblicato", "Published"], yours: ["Tuo", "Yours"],
  analyzed: ["Analizzato", "Analyzed"], required: ["Richiesto", "Required"], optional: ["Opzionale", "Optional"],
  // Catalog
  searchPlaceholder: ["Cerca per nome prodotto o produttore…", "Search by product or manufacturer…"],
  noResults: ["Nessun prodotto trovato.", "No products found."],
  yourCatalog: ["Il tuo catalogo prodotti", "Your product catalog"],
  explore: ["Esplora", "Explore"],
  // Categories
  all: ["Tutti", "All"], insulation: ["Isolanti", "Insulation"], masonry: ["Muratura", "Masonry"],
  structural: ["Strutturali", "Structural"], windows: ["Serramenti", "Windows"],
  cladding: ["Rivestimenti", "Cladding"], waterproofing: ["Impermeabilizzazione", "Waterproofing"],
  // Product fields
  productInfo: ["Informazioni Prodotto", "Product Information"], productName: ["Nome Prodotto", "Product Name"],
  uid: ["Identificatore Univoco (UID)", "Unique Identifier (UID)"], itemType: ["Tipo Item", "Item Type"],
  product: ["Prodotto", "Product"], cprCat: ["Categoria CPR", "CPR Category"],
  funcUnit: ["Unità Funzionale", "Functional Unit"], description: ["Descrizione", "Description"],
  dimensions: ["Dimensioni standard (LxPxH)", "Standard Dimensions (LxDxH)"], weight: ["Peso", "Weight"],
  manufacturer: ["Produttore", "Manufacturer"], company: ["Azienda", "Company"],
  legalHQ: ["Sede legale", "Legal Headquarters"], prodSite: ["Sito produttivo", "Production Site"],
  website: ["Sito web", "Website"], dataContact: ["Contatto responsabile dati", "Data Contact Person"],
  companyCerts: ["Certificazioni azienda", "Company Certifications"],
  optionalInfo: ["Informazioni Opzionali", "Optional Information"],
  batchSerial: ["Numero Lotto / Serie", "Batch / Serial Number"], prodImage: ["Immagine prodotto", "Product Image"],
  saleType: ["Tipo vendita", "Sale Type"], mfgDate: ["Data produzione", "Manufacturing Date"],
  // Performance
  mechPerf: ["Prestazioni Meccaniche", "Mechanical Performance"],
  compStrength: ["Resistenza a compressione", "Compressive Strength"],
  flexStrength: ["Resistenza a flessione", "Flexural Strength"],
  tensStrength: ["Resistenza a trazione", "Tensile Strength"],
  elastMod: ["Modulo di elasticità", "Elasticity Modulus"],
  impactRes: ["Resistenza all'urto", "Impact Resistance"],
  thermPerf: ["Prestazioni Termiche", "Thermal Performance"],
  thermCond: ["Conducibilità termica (λ)", "Thermal Conductivity (λ)"],
  thermRes: ["Resistenza termica (R)", "Thermal Resistance (R)"],
  fireClass: ["Classe di reazione al fuoco", "Fire Reaction Class"],
  expCoeff: ["Coefficiente di espansione", "Expansion Coefficient"],
  acoustics: ["Acustica", "Acoustics"],
  soundAbs: ["Coefficiente assorbimento acustico", "Sound Absorption Coefficient"],
  soundIns: ["Potere fonoisolante", "Sound Insulation Rating"],
  moisture: ["Acqua e Umidità", "Moisture & Water"],
  waterAbs: ["Assorbimento acqua", "Water Absorption"],
  vaporPerm: ["Permeabilità al vapore (μ)", "Vapor Permeability (μ)"],
  freezeThaw: ["Resistenza cicli gelo-disgelo", "Freeze-Thaw Resistance"],
  compliant: ["Conforme", "Compliant"],
  durability: ["Durabilità e Resistenza Ambientale", "Durability & Environmental Resistance"],
  uvRes: ["Resistenza UV", "UV Resistance"], corrRes: ["Resistenza corrosione", "Corrosion Resistance"],
  chemRes: ["Resistenza agenti chimici", "Chemical Resistance"],
  // Compliance
  declarations: ["Dichiarazioni di Prestazione e Conformità", "Declarations of Performance & Conformity"],
  dopLabel: ["Dichiarazione di Prestazione (DoP)", "Declaration of Performance (DoP)"],
  refStandard: ["Standard di riferimento", "Reference Standard"],
  docLabel: ["Dichiarazione di Conformità (DoC)", "Declaration of Conformity (DoC)"],
  ceMark: ["Marcatura CE", "CE Marking"], qc: ["Controllo qualità", "Quality Control"],
  prodSafety: ["Sicurezza del Prodotto", "Product Safety"],
  cmr: ["Contiene sostanze CMR?", "Contains CMR substances?"],
  svhc: ["Contiene sostanze SVHC?", "Contains SVHC substances?"],
  pentane: ["Contiene pentano?", "Contains pentane?"],
  pfas: ["Contiene PFAS?", "Contains PFAS?"],
  flameRet: ["Ritardanti di fiamma?", "Flame retardants?"],
  rohs: ["Conforme RoHS?", "RoHS Compliant?"],
  childLabor: ["Conforme Child Labor Regulation?", "Child Labor Regulation Compliant?"],
  prodCerts: ["Certificazioni Prodotto", "Product Certifications"],
  compCerts: ["Certificazioni Aziendali", "Company Certifications"],
  // Documents
  analyzedDocs: ["Documenti Analizzati", "Analyzed Documents"],
  techDocs: ["Documentazione Tecnica", "Technical Documentation"],
  otherDecl: ["Altre Dichiarazioni", "Other Declarations"],
  fieldsExtracted: ["campi estratti", "fields extracted"],
  uploadMore: ["Carica documenti aggiuntivi", "Upload additional documents"],
  dropFiles: ["Trascina qui i nuovi documenti", "Drop new documents here"],
  missingClick: ["Dato mancante — clicca per inserire", "Missing data — click to enter"],
  source: ["Fonte", "Source"],
  // Lifecycle
  production: ["Produzione", "Production"], distribution: ["Distribuzione", "Distribution"],
  use: ["Uso", "Use"], endOfLife: ["Fine vita", "End of Life"],
  rawMaterials: ["Materie Prime", "Raw Materials"], transport: ["Trasporto", "Transport"],
  manufacturing: ["Manifattura", "Manufacturing"], installation: ["Installazione", "Installation"],
  maintenance: ["Manutenzione", "Maintenance"], replacement: ["Sostituzione", "Replacement"],
  energyWater: ["Energia/Acqua", "Energy/Water"], deconstruction: ["Decostruzione", "Deconstruction"],
  processing: ["Trattamento", "Processing"],
  dataNotAvail: ["Dati non disponibili", "Data not available"],
  notFilledIn: ["Non compilato", "Not filled in"],
  // Version history
  versionHistory: ["Cronologia Versioni", "Version History"],
  firstRelease: ["Prima release", "First release"], current: ["Corrente", "Current"],
  // Export
  freePlan: ["Piano gratuito", "Free plan"],
  upgradeMsg: ["Passa a Starter per esportare e condividere", "Upgrade to Starter to export and share"],
  unlockFrom: ["Pubblica", "Publish"],
  downloadPDF: ["Scarica PDF", "Download PDF"], share: ["Condividi", "Share"],
  print: ["Stampa", "Print"], starterActive: ["Piano Starter Attivo", "Starter Plan Active"],
  exportEnabled: ["Export e condivisione abilitati", "Export & share enabled"],
  // Composition
  productStructure: ["Struttura Prodotto", "Product Structure"],
  mainProduct: ["Prodotto principale", "Main product"],
  linked: ["collegati", "linked"],
  searchCatalog: ["Cerca nel catalogo…", "Search catalog…"],
  noResultsCat: ["Nessun risultato", "No results"],
  linkBtn: ["Collega", "Link"],
  addComponent: ["Aggiungi componente", "Add component"],
  distResp: ["Responsabilità distribuita", "Distributed responsibility"],
  distRespDesc: ["Ogni componente collegato mantiene il proprietario originale come responsabile.", "Each linked component retains its original owner as responsible."],
  withoutDPP: ["senza DPP associato", "without linked DPP"],
  inviteSupplier: ["Invita il fornitore di ", "Invite supplier for "],
  supplierEmail: ["Email fornitore", "Supplier email"],
  manuallyAdded: ["Inserito manualmente", "Manually added"],
  // Published view
  envImpact: ["Impatto Ambientale (GWP)", "Environmental Impact (GWP)"],
  gwpByStage: ["GWP per fase del ciclo di vita", "GWP by lifecycle stage"],
  gwpTotal: ["GWP Totale (A1-D)", "Total GWP (A1-D)"],
  matComposition: ["Composizione Materiali", "Material Composition"],
  recycled: ["Riciclato", "Recycled"], energy: ["Energia", "Energy"],
  content: ["contenuto", "content"], eol: ["fine vita", "end of life"], cls: ["classe", "class"],
  // Signup
  createAccount: ["Crea il tuo account DeePPy", "Create your DeePPy account"],
  fullName: ["Nome completo", "Full name"], businessEmail: ["Email aziendale", "Business email"],
  companyVat: ["Azienda o partita IVA", "Company or VAT number"],
  createFreeAcc: ["Crea account gratuito", "Create free account"],
  alreadyAccount: ["Hai già un account? Accedi", "Already have an account? Log in"],
  autoExtraction: ["Estrazione automatica dai documenti", "Automatic extraction from documents"],
  completeView: ["Visualizzazione completa senza limiti", "Complete view with no limits"],
  esprCompliant: ["Conforme ESPR EU 2024/1781", "ESPR EU 2024/1781 compliant"],
  noCreditCard: ["Nessuna carta di credito richiesta", "No credit card required"],
  companyName: ["Nome azienda", "Company name"],
  yourRole: ["Il tuo ruolo", "Your role"],
  prodArea: ["Ambito produzione", "Production area"],
  consultant: ["Consulente", "Consultant"], distributor: ["Distributore", "Distributor"], other: ["Altro", "Other"],
  binders: ["Leganti", "Binders"],
  // Onboarding
  uploadDocs: ["Carica i tuoi documenti", "Upload your documents"],
  uploadDesc: ["Carica qui DoP, schede tecniche, EPD, certificati. DeePPy li analizza e compila la scheda prodotto.", "Upload your DoP, technical sheets, EPD, certificates. DeePPy analyzes them and fills the product sheet."],
  dropPDF: ["Trascina qui i tuoi file PDF", "Drop your PDF files here"],
  orBrowse: ["oppure sfoglia", "or browse"],
  generatePassport: ["Genera il Passaporto", "Generate Passport"],
  // Field labels
  fProductName: ["Nome Prodotto", "Product Name"],
  fItemType: ["Tipo articolo", "Item Type"],
  fCprCategory: ["Categoria CPR", "CPR Category"],
  fFuncUnit: ["Unità Funzionale", "Functional Unit"],
  fDescription: ["Descrizione", "Description"],
  fDimensions: ["Dimensioni standard (LxPxH)", "Standard Dimensions (LxDxH)"],
  fWeight: ["Peso", "Weight"],
  fCompany: ["Azienda", "Company"],
  fLegalHQ: ["Sede legale", "Legal Headquarters"],
  fProdSite: ["Sito produttivo", "Production Site"],
  fWebsite: ["Sito web", "Website"],
  fDataContact: ["Contatto responsabile dati", "Data Contact Person"],
  fCompCerts: ["Certificazioni azienda", "Company Certifications"],
  fBatchSerial: ["Numero Lotto / Serie", "Batch / Serial Number"],
  fProdImage: ["Immagine prodotto", "Product Image"],
  fSaleType: ["Tipo vendita", "Sale Type"],
  fMfgDate: ["Data produzione", "Manufacturing Date"],
  fCompStrength: ["Resistenza a compressione", "Compressive Strength"],
  fFlexStrength: ["Resistenza a flessione", "Flexural Strength"],
  fTensStrength: ["Resistenza a trazione", "Tensile Strength"],
  fElastMod: ["Modulo di elasticità", "Elasticity Modulus"],
  fImpactRes: ["Resistenza all'urto", "Impact Resistance"],
  fThermCond: ["Conducibilità termica (λ)", "Thermal Conductivity (λ)"],
  fThermRes: ["Resistenza termica (R)", "Thermal Resistance (R)"],
  fFireClass: ["Classe reazione al fuoco", "Fire Reaction Class"],
  fExpCoeff: ["Coefficiente di espansione", "Expansion Coefficient"],
  fSoundAbs: ["Coeff. assorbimento acustico", "Sound Absorption Coefficient"],
  fSoundIns: ["Potere fonoisolante", "Sound Insulation Rating"],
  fWaterAbs: ["Assorbimento acqua", "Water Absorption"],
  fVaporPerm: ["Permeabilità al vapore (μ)", "Vapor Permeability (μ)"],
  fFreezeThaw: ["Resistenza gelo-disgelo", "Freeze-Thaw Resistance"],
  fUvRes: ["Resistenza UV", "UV Resistance"],
  fCorrRes: ["Resistenza corrosione", "Corrosion Resistance"],
  fChemRes: ["Resistenza agenti chimici", "Chemical Resistance"],
  fDoP: ["Dichiarazione di Prestazione (DoP)", "Declaration of Performance (DoP)"],
  fRefStandard: ["Standard di riferimento", "Reference Standard"],
  fDoC: ["Dichiarazione di Conformità (DoC)", "Declaration of Conformity (DoC)"],
  fCeMark: ["Marcatura CE", "CE Marking"],
  fQC: ["Controllo qualità", "Quality Control"],
  fCmr: ["Contiene sostanze CMR?", "Contains CMR substances?"],
  fSvhc: ["Contiene sostanze SVHC?", "Contains SVHC substances?"],
  fPentane: ["Contiene pentano?", "Contains pentane?"],
  fPfas: ["Contiene PFAS?", "Contains PFAS?"],
  fFlameRet: ["Ritardanti di fiamma?", "Flame retardants?"],
  fRohs: ["Conforme RoHS?", "RoHS Compliant?"],
  fChildLabor: ["Conforme regolamento lavoro minorile?", "Child Labor Regulation Compliant?"],
  fInstMethod: ["Istruzioni di installazione", "Method Statement — Installation"],
  fMaintMethod: ["Istruzioni di manutenzione", "Method Statement — Maintenance"],
  fDraw2d: ["Disegno 2D", "2D Drawing"],
  fDraw3d: ["Modello 3D (BIM)", "3D Model (BIM)"],
  fClimateDecl: ["Dichiarazione climatica", "Climate Declaration"],
  fOtherDoc: ["Altra documentazione", "Other documentation"],
};
const t = (key, lang) => { const v = i18n[key]; return v ? (lang === "it" ? v[0] : v[1]) : key; };

// ─── COLLAPSIBLE SECTION ─────────────────────────────────
const ColSec = ({ title, iconD, defaultOpen = true, badge, children }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden", marginBottom: 12 }}>
      <button onClick={() => setOpen(!open)} style={{ width: "100%", padding: "12px 16px", display: "flex", alignItems: "center", gap: 7, background: "none", border: "none", borderBottom: open ? `1px solid ${T.borderLight}` : "none", cursor: "pointer", fontFamily: font, textAlign: "left" }}>
        <I d={open ? ic.chevDown : ic.chevRight} size={14} color={T.textSec} />
        {iconD && <I d={iconD} size={15} color={T.accentDark} />}
        <span style={{ fontSize: 14, fontWeight: 700, color: T.textDark, flex: 1 }}>{title}</span>
        {badge}
      </button>
      {open && <div style={{ padding: "14px 16px" }}>{children}</div>}
    </div>
  );
};

// ─── SUPPLY CHAIN MAP (SVG) ──────────────────────────────
const supplyPoints = [
  { name: "Levery srl (Manufacturer)", city: "Rimini, IT", lat: 44.06, lng: 12.57, type: "producer" },
  { name: "Arpa Industriale", city: "Bra, IT", lat: 44.70, lng: 7.85, type: "supplier" },
  { name: "Rockwool Italia", city: "Porcari, IT", lat: 43.84, lng: 10.62, type: "supplier" },
  { name: "Metra SpA", city: "Rodengo-Saiano, IT", lat: 45.59, lng: 10.11, type: "supplier" },
  { name: "BASF SE (Additives)", city: "Ludwigshafen, DE", lat: 49.48, lng: 8.44, type: "supplier" },
];
function SupplyMap({ dppData }) {
  const [hover, setHover] = useState(null);
  const toX = lng => ((lng + 12) / 36) * 360 + 20;
  const toY = lat => ((58 - lat) / 22) * 210 + 5;

  // When real passport data exists, show the actual supply chain derived from
  // the manufacturer + Bill-of-Materials suppliers (no fake map — we have no
  // geocoordinates, so we list real names/addresses instead).
  const _pp = dppData?.passport;
  if (_pp) {
    const mv = (o, f) => { const x = o?.[f]; return (x && typeof x === "object") ? x.value : x; };
    const clean = (s) => (s && String(s).trim() && String(s).trim() !== "-") ? String(s).trim() : "";
    const mfr = _pp.overview?.manufacturer || {};
    const mfrName = clean(mfr.company_name?.value);
    const mfrAddr = clean(mfr.manufacturing_site?.value) || clean(mfr.address?.value);
    const suppliers = [];
    (_pp.composition?.materials || []).forEach((m) => {
      (m.suppliers || []).forEach((s) => {
        const name = clean(mv(s, "name"));
        const addr = clean(mv(s, "address"));
        const transport = clean(mv(s, "transport_method"));
        const dist = clean(mv(s, "distance_km"));
        if (name || addr) {
          suppliers.push({
            label: name || clean(mv(m, "description")) || "Supplier",
            addr, transport, dist,
            material: clean(mv(m, "description")),
          });
        }
      });
    });
    return (
      <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden", padding: "14px 16px" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.textDark, marginBottom: 10, display: "flex", alignItems: "center", gap: 6 }}><I d={ic.factory} size={14} color={T.accentDark} /> Supply Chain</div>
        {mfrName && (
          <div style={{ display: "flex", alignItems: "flex-start", gap: 8, padding: "8px 10px", borderRadius: 8, background: T.accentSoft + "40", marginBottom: 8 }}>
            <I d={ic.box} size={13} color={T.accentDark} />
            <div><div style={{ fontSize: 12, fontWeight: 700, color: T.textDark }}>{mfrName}</div>{mfrAddr && <div style={{ fontSize: 11, color: T.textSec }}>{mfrAddr}</div>}<div style={{ fontSize: 10, color: T.accentDark, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em", marginTop: 2 }}>Manufacturer</div></div>
          </div>
        )}
        {suppliers.length > 0 ? suppliers.map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, padding: "7px 10px", borderBottom: i < suppliers.length - 1 ? `1px solid ${T.borderLight}` : "none" }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: T.navy, marginTop: 5, flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: T.textDark }}>{s.label}{s.material && s.label !== s.material ? <span style={{ fontWeight: 400, color: T.textSec }}> — {s.material}</span> : null}</div>
              {s.addr && <div style={{ fontSize: 11, color: T.textSec }}>{s.addr}</div>}
              {(s.transport || s.dist) && <div style={{ fontSize: 10, color: T.textSec }}>{[s.transport, s.dist ? `${s.dist} km` : ""].filter(Boolean).join(" · ")}</div>}
            </div>
          </div>
        )) : (!mfrName && (
          <div style={{ fontSize: 12, color: T.textSec, fontStyle: "italic", padding: "8px 0" }}>No supply-chain data extracted from the documents.</div>
        ))}
      </div>
    );
  }

  return (
    <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden" }}>
      <div style={{ display: "flex" }}>
        <div style={{ flex: 1, padding: 12 }}>
          <svg viewBox="0 0 400 220" style={{ width: "100%", height: 190 }}>
            {/* EU map outline - simplified */}
            <path d="M80,20 L100,15 L130,12 L165,10 L200,8 L240,10 L275,15 L310,12 L340,18 L360,30 L370,50 L375,75 L372,100 L365,125 L350,148 L330,165 L305,175 L275,182 L240,185 L205,183 L175,178 L145,170 L120,158 L100,142 L85,122 L75,98 L72,72 L75,48 L78,32 Z" fill={T.bgSoft} stroke={T.border} strokeWidth={1.5} />
            {/* Country borders hint */}
            <path d="M200,40 L210,80 L240,100 L220,140 L190,155 L160,135 L170,95 L200,40" fill="none" stroke={T.borderLight} strokeWidth={0.8} />
            <path d="M240,30 L260,50 L280,45 L300,60 L290,90 L260,80 L240,55 Z" fill="none" stroke={T.borderLight} strokeWidth={0.8} />
            {/* Italy shape hint */}
            <path d="M210,95 L220,110 L225,130 L218,150 L210,165 L205,155 L208,135 L205,115 L210,95" fill={T.accentSoft+"60"} stroke={T.accent} strokeWidth={0.8} />
            {/* Connection lines from manufacturer to suppliers */}
            {supplyPoints.filter(p => p.type === "supplier").map((p, i) => (
              <line key={i} x1={toX(supplyPoints[0].lng)} y1={toY(supplyPoints[0].lat)} x2={toX(p.lng)} y2={toY(p.lat)} stroke={T.accent} strokeWidth={1.5} strokeDasharray="4,3" opacity={0.4} />
            ))}
            {/* Points */}
            {supplyPoints.map((p, i) => (
              <g key={i} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)} style={{ cursor: "pointer" }}>
                {p.type === "producer" && <circle cx={toX(p.lng)} cy={toY(p.lat)} r={12} fill={T.accent} opacity={0.15} />}
                <circle cx={toX(p.lng)} cy={toY(p.lat)} r={hover === i ? 7 : 5} fill={p.type === "producer" ? T.accent : T.navy} stroke={T.bg} strokeWidth={2} />
                {hover === i && (
                  <g>
                    <rect x={toX(p.lng) - 65} y={toY(p.lat) - 30} width={130} height={24} rx={4} fill={T.navy} opacity={0.92} />
                    <text x={toX(p.lng)} y={toY(p.lat) - 15} textAnchor="middle" fontSize={9} fill={T.text} fontFamily={font}>{p.name}</text>
                  </g>
                )}
              </g>
            ))}
          </svg>
        </div>
        <div style={{ width: 200, padding: "14px 16px", borderLeft: `1px solid ${T.border}`, display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: T.textDark, marginBottom: 2 }}>Supply Chain</div>
          {[["EU Suppliers", "100%", T.accent], ["Avg. Distance", "320 km", T.textSec], ["Countries", "2 (IT, DE)", T.textSec], ["Within 500km", "3/4 (75%)", T.accent]].map(([l, v, c], i) => (
            <div key={i}><div style={{ fontSize: 10, color: T.textSec, textTransform: "uppercase", fontWeight: 600, letterSpacing: "0.05em" }}>{l}</div><div style={{ fontSize: 14, fontWeight: 700, color: c }}>{v}</div></div>
          ))}
          <Badge color={T.accentDark} bg={T.accentSoft}><I d={ic.check} size={9} color={T.accentDark} /> 100% EU Supply Chain</Badge>
        </div>
      </div>
    </div>
  );
}

// ─── CATALOG DATA (shared across views) ─────────────────
// Catalog rows come from GET /api/catalog (real published products across all
// companies). The static demo array previously here is gone — `CatalogView`
// fetches on mount. Category chips are derived from the actual data; we still
// keep "all" as a special key meaning no filter.
const CATALOG_ALL_KEY = "all";

function Sidebar({ activePage, onNavigate, L, onLogout }) {
  const t = (it, en) => L?.lang === "it" ? it : en;
  const nav = (pg) => onNavigate && onNavigate(pg);
  const [companyName, setCompanyName] = useState("");
  const [me, setMe] = useState(null);
  useEffect(() => {
    fetch("/api/company", { credentials: "include" }).then(r => r.json()).then(c => { if (c && c.name) setCompanyName(c.name); }).catch(() => {});
    fetch("/api/auth/me", { credentials: "include" }).then(r => r.ok ? r.json() : null).then(d => { if (d?.user) setMe(d.user); }).catch(() => {});
  }, []);
  const doLogout = async () => {
    try { await fetch("/api/auth/logout", { method: "POST", credentials: "include" }); } catch {}
    if (onLogout) onLogout(); else window.location.reload();
  };
  const displayName = me?.name || (me?.email ? me.email.split("@")[0] : "—");
  const initials = (displayName || "?").split(/[\s.@]+/).filter(Boolean).slice(0, 2).map(s => s[0]?.toUpperCase()).join("") || "U";
  const roleLabel = me?.role ? me.role.charAt(0).toUpperCase() + me.role.slice(1) : "";
  return (
    <nav style={{ width: 192, background: T.navy, display: "flex", flexDirection: "column", flexShrink: 0 }}>
      <div style={{ padding: "16px 14px 6px" }}><Logo size={20} withText /><div style={{ fontSize: 9, color: T.textMuted, marginTop: 4 }}>Digital Product Passport</div></div>
      <div style={{ padding: "8px 12px", borderBottom: `1px solid ${T.navyMid}`, marginBottom: 4 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: T.textMuted }}>{companyName || "—"}</div>
        {roleLabel && <div style={{ fontSize: 9, color: T.textMuted, opacity: 0.5 }}>{roleLabel}</div>}
      </div>
      <div style={{ padding: "0 6px", flex: 1 }}>
        <div style={{ fontSize: 9, fontWeight: 700, color: T.textMuted, opacity: 0.4, textTransform: "uppercase", letterSpacing: "0.1em", padding: "6px 8px 3px" }}>Menu</div>
        {[[ic.home, "Dashboard", "dashboard"], [ic.plus, t("Nuovo","New"), "onboard"], [ic.search, t("Catalogo","Catalog"), "catalog"], [ic.clip, t("Progetti","Projects"), "projects"], [ic.file, t("Documenti","Documents"), "documents"]].map(([d, lb, pg], i) => {
          const active = activePage === pg;
          return (
            <button key={i} onClick={() => nav(pg)} style={{ width: "100%", display: "flex", alignItems: "center", gap: 7, padding: "8px 8px", borderRadius: 5, border: "none", background: active ? T.navyLight : "transparent", color: active ? T.text : T.textMuted, fontSize: 12, fontWeight: active ? 600 : 400, cursor: "pointer", textAlign: "left", marginBottom: 1, fontFamily: font }}>
              <I d={d} size={14} color={active ? T.accent : T.textMuted} />{lb}
            </button>
          );
        })}
        <div style={{ fontSize: 9, fontWeight: 700, color: T.textMuted, opacity: 0.4, textTransform: "uppercase", letterSpacing: "0.1em", padding: "14px 8px 3px" }}>{t("Amministrazione","Administration")}</div>
        {[[ic.users, "Team", "team"], [ic.settings, t("Impostazioni","Settings"), "settings"]].map(([d, lb, pg], i) => {
          const active = activePage === pg;
          return (
            <button key={i} onClick={() => nav(pg)} style={{ width: "100%", display: "flex", alignItems: "center", gap: 7, padding: "7px 8px", borderRadius: 5, border: "none", background: active ? T.navyLight : "transparent", color: active ? T.text : T.textMuted, fontSize: 11, cursor: "pointer", textAlign: "left", fontFamily: font, fontWeight: active ? 600 : 400 }}>
              <I d={d} size={13} color={active ? T.accent : T.textMuted} />{lb}
            </button>
          );
        })}
      </div>
      <div style={{ padding: "10px 12px", borderTop: `1px solid ${T.navyMid}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8 }}>
          <div style={{ width: 26, height: 26, borderRadius: "50%", background: T.accentDark, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: T.text }}>{initials}</div>
          <div style={{ flex: 1, minWidth: 0 }}><div style={{ fontSize: 11, fontWeight: 600, color: T.text, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{displayName}</div><div style={{ fontSize: 9, color: T.textMuted, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{me?.email || ""}</div></div>
        </div>
        <button onClick={doLogout} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 6, padding: "6px 0", borderRadius: 5, border: `1px solid ${T.navyMid}`, background: "transparent", color: T.textMuted, fontSize: 11, cursor: "pointer", fontFamily: font }}><I d={ic.arrow} size={12} color={T.textMuted} style={{ transform: "rotate(180deg)" }} />{t("Esci","Sign out")}</button>
      </div>
    </nav>
  );
}

// Lightweight markdown renderer for assistant replies — supports **bold**,
// [text](url), `code`, and "- " / "* " bullets. Handles blank lines as
// paragraph spacing. Intentionally minimal: no heavy dependencies.
const _MdInline = ({ text }) => {
  if (!text) return null;
  const parts = [];
  const re = /\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)\s]+)\)|`([^`]+)`/g;
  let i = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > i) parts.push(text.slice(i, m.index));
    if (m[1] != null) parts.push(<strong key={parts.length}>{m[1]}</strong>);
    else if (m[2] != null) parts.push(<a key={parts.length} href={m[3]} target="_blank" rel="noopener noreferrer" style={{ color: "inherit", textDecoration: "underline" }}>{m[2]}</a>);
    else if (m[4] != null) parts.push(<code key={parts.length} style={{ background: "rgba(0,0,0,0.07)", padding: "1px 4px", borderRadius: 3, fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace", fontSize: "0.9em" }}>{m[4]}</code>);
    i = m.index + m[0].length;
  }
  if (i < text.length) parts.push(text.slice(i));
  return <>{parts}</>;
};

const Markdown = ({ text }) => {
  if (!text) return null;
  const lines = String(text).split("\n");
  return lines.map((line, i) => {
    if (!line.trim()) return <div key={i} style={{ height: 6 }} />;
    const bm = /^\s*[-*]\s+(.*)/.exec(line);
    if (bm) {
      return (
        <div key={i} style={{ display: "flex", gap: 6, paddingLeft: 2 }}>
          <span style={{ color: "currentColor", opacity: 0.55 }}>•</span>
          <span style={{ flex: 1 }}><_MdInline text={bm[1]} /></span>
        </div>
      );
    }
    return <div key={i}><_MdInline text={line} /></div>;
  });
};

function ChatPanel({ open, onClose, L, productId }) {
  const it = L?.lang === "it";
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [available, setAvailable] = useState(true);
  const scrollRef = useRef(null);

  // Load the persisted conversation when the panel opens for a product.
  useEffect(() => {
    if (!open || !productId) return;
    fetch(`/api/products/${productId}/chat`, { credentials: "include" })
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (!d) return;
        setAvailable(d.available !== false);
        setMsgs(Array.isArray(d.messages) ? d.messages : []);
      })
      .catch(() => {});
  }, [open, productId]);

  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight; }, [msgs, busy]);

  const startNew = async () => {
    if (busy || !productId) return;
    try {
      await fetch(`/api/products/${productId}/chat/new`, { method: "POST", credentials: "include" });
    } catch {}
    setMsgs([]); setInput("");
  };

  const send = async () => {
    const text = input.trim();
    if (!text || busy || !productId) return;
    setInput("");
    setMsgs(p => [...p, { from: "user", text }]);
    setBusy(true);
    try {
      const res = await fetch(`/api/products/${productId}/chat`, {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const d = await res.json();
      if (!res.ok) {
        setMsgs(p => [...p, { from: "agent", text: d.detail || (it ? "Errore dell'assistente." : "Assistant error.") }]);
        if (res.status === 503) setAvailable(false);
      } else {
        setMsgs(p => [...p, { from: "agent", text: d.reply }]);
      }
    } catch {
      setMsgs(p => [...p, { from: "agent", text: it ? "Errore di connessione." : "Connection error." }]);
    } finally {
      setBusy(false);
    }
  };

  if (!open) return null;
  return (
    <div style={{ width: 340, borderLeft: `1px solid ${T.border}`, background: T.bg, display: "flex", flexDirection: "column", flexShrink: 0 }}>
      <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 26, height: 26, borderRadius: "50%", background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.msg} size={12} color={T.accent} /></div>
          <div><div style={{ fontSize: 12, fontWeight: 700, color: T.textDark }}>{it?"Assistente DeePPy":"DeePPy Assistant"}</div><div style={{ fontSize: 9, color: available?T.accent:T.textSec, fontWeight: 600 }}>{available?(it?"Attivo":"Active"):(it?"Non configurato":"Not configured")}</div></div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <button onClick={startNew} disabled={busy} title={it?"Nuova chat":"New chat"} style={{ display: "flex", alignItems: "center", gap: 4, background: "none", border: `1px solid ${T.border}`, borderRadius: 6, cursor: busy?"default":"pointer", padding: "4px 8px", fontFamily: font, fontSize: 11, color: T.textSec }}><I d={ic.plus} size={12} color={T.textSec} /> {it?"Nuova":"New"}</button>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", padding: 2 }}><I d={ic.x} size={16} color={T.textSec} /></button>
        </div>
      </div>
      <div ref={scrollRef} style={{ flex: 1, overflowY: "auto", padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
        {msgs.length === 0 && !busy && (
          <div style={{ fontSize: 12, color: T.textSec, lineHeight: 1.55, padding: "8px 4px" }}>
            {available
              ? (it ? "Chiedimi qualsiasi cosa su questo prodotto — composizione, prestazioni, conformità, impatto ambientale…" : "Ask me anything about this product — composition, performance, compliance, environmental impact…")
              : (it ? "Assistente non configurato (manca OPENAI_API_KEY)." : "Assistant not configured (missing OPENAI_API_KEY).")}
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} style={{ alignSelf: m.from === "user" ? "flex-end" : "flex-start", maxWidth: "88%", padding: "9px 13px", borderRadius: m.from === "user" ? "10px 10px 2px 10px" : "10px 10px 10px 2px", background: m.from === "user" ? T.navy : T.bgSoft, color: m.from === "user" ? T.text : T.textDark, fontSize: 12, lineHeight: 1.55, border: m.from === "agent" ? `1px solid ${T.border}` : "none", whiteSpace: m.from === "user" ? "pre-wrap" : "normal" }}>{m.from === "agent" ? <Markdown text={m.text} /> : m.text}</div>
        ))}
        {busy && <div style={{ alignSelf: "flex-start", padding: "9px 13px", borderRadius: "10px 10px 10px 2px", background: T.bgSoft, color: T.textSec, fontSize: 12, border: `1px solid ${T.border}` }}>{it?"Sto pensando…":"Thinking…"}</div>}
      </div>
      <div style={{ padding: 10, borderTop: `1px solid ${T.border}` }}>
        <div style={{ display: "flex", gap: 6, padding: "8px 10px", borderRadius: 8, border: `1px solid ${T.border}`, opacity: available?1:0.5 }}>
          <input value={input} disabled={!available || busy} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()} placeholder={it?"Chiedi all'assistente…":"Ask the assistant…"} style={{ flex: 1, border: "none", outline: "none", fontSize: 12, background: "transparent", fontFamily: font }} />
          <button onClick={send} disabled={!available || busy} style={{ width: 26, height: 26, borderRadius: 6, background: T.accent, border: "none", cursor: available&&!busy?"pointer":"default", display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.arrow} size={13} color={T.navy} /></button>
        </div>
      </div>
    </div>
  );
}


// ─── LANDING ─────────────────────────────────────────────
function SignupPage({ onNavigate, L, onAuth }) {
  const it = L?.lang === "it";
  const [mode, setMode] = useState("login"); // "login" or "register"
  const [form, setForm] = useState({ name: "", company: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const track = (ev, data = {}) => { if (window.posthog) window.posthog.capture(ev, data); console.log("[track]", ev, data); };
  const inp = (label, key, type = "text", ph = "") => (
    <div style={{ marginBottom: 14 }}><label style={{ fontSize: 12, fontWeight: 600, color: T.textSec, display: "block", marginBottom: 4 }}>{label}</label><input type={type} placeholder={ph} value={form[key] || ""} onChange={(e) => setForm({ ...form, [key]: e.target.value })} onKeyDown={(e) => e.key === "Enter" && (mode === "login" ? doLogin() : doRegister())} style={{ width: "100%", padding: "10px 12px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 14, outline: "none", boxSizing: "border-box", fontFamily: font }} /></div>
  );

  const doLogin = async () => {
    setError(""); setBusy(true); track("login_attempted");
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || (it ? "Accesso fallito" : "Login failed")); return; }
      if (onAuth) onAuth(data.user); else onNavigate("dashboard");
    } catch { setError(it ? "Errore di connessione" : "Connection error"); }
    finally { setBusy(false); }
  };

  const doRegister = async () => {
    setError("");
    if (!form.company || !form.email || !form.password) { setError(it ? "Compila tutti i campi" : "Fill in all fields"); return; }
    if (form.password.length < 8) { setError(it ? "La password deve avere almeno 8 caratteri" : "Password must be at least 8 characters"); return; }
    setBusy(true); track("signup_attempted");
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company_name: form.company, email: form.email, password: form.password, name: form.name }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || (it ? "Registrazione fallita" : "Registration failed")); return; }
      if (onAuth) onAuth(data.user); else onNavigate("dashboard");
    } catch { setError(it ? "Errore di connessione" : "Connection error"); }
    finally { setBusy(false); }
  };

  const ErrorBox = () => error ? <div style={{ marginBottom: 14, padding: "9px 12px", borderRadius: 6, background: "#FEF2F2", border: "1px solid #FECACA", color: "#B91C1C", fontSize: 12.5 }}>{error}</div> : null;
  return (
    <div style={{ fontFamily: font, minHeight: "100vh", display: "flex" }}>
      <div style={{ width: 420, background: T.navy, padding: "56px 44px", display: "flex", flexDirection: "column", justifyContent: "center", flexShrink: 0 }}>
        <Logo size={22} withText />
        <h2 style={{ fontSize: 26, fontWeight: 800, color: T.text, marginTop: 28, lineHeight: 1.3 }}>{it ? "Il passaporto digitale dei tuoi prodotti da costruzione." : "The digital passport for your construction products."}</h2>
        <p style={{ fontSize: 14, color: T.textMuted, lineHeight: 1.6, marginTop: 10 }}>{it ? "Carica i documenti tecnici. Le informazioni vengono estratte e organizzate. Tu verifichi e pubblichi." : "Upload technical documents. Information is extracted and organized. You verify and publish."}</p>
        <div style={{ marginTop: 32 }}>
          {(it ? ["Estrazione automatica dai documenti","Vista completa senza limiti","Allineato a ESPR EU 2024/1781","Nessuna carta di credito richiesta"] : ["Automatic extraction from documents","Complete view with no limits","ESPR EU 2024/1781 compliant","No credit card required"]).map((f,i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}><I d={ic.check} size={14} color={T.accent} /><span style={{ fontSize: 13, color: T.textMuted }}>{f}</span></div>
          ))}
        </div>
        <button onClick={() => onNavigate("landing")} style={{ marginTop: 32, background: "none", border: "none", color: T.textMuted, fontSize: 12, cursor: "pointer", fontFamily: font, display: "flex", alignItems: "center", gap: 6 }}><I d={ic.arrow} size={12} color={T.textMuted} style={{ transform: "rotate(180deg)" }} /> {it ? "Torna alla homepage" : "Back to homepage"}</button>
      </div>
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 48, background: T.bg }}>
        <div style={{ width: "100%", maxWidth: 380 }}>
          {mode === "login" ? (
            <>
              <h2 style={{ fontSize: 24, fontWeight: 800, color: T.navy, marginBottom: 4 }}>{it ? "Accedi" : "Sign in"}</h2>
              <p style={{ fontSize: 13, color: T.textSec, marginBottom: 24 }}>{it ? "Inserisci le tue credenziali per accedere alla piattaforma." : "Enter your credentials to access the platform."}</p>
              <ErrorBox />
              {inp(it ? "Email aziendale" : "Business email", "email", "email", "mario.rossi@azienda.it")}
              {inp("Password", "password", "password", "")}
              <Btn primary onClick={doLogin} style={{ width: "100%", opacity: busy ? 0.6 : 1 }}>{busy ? (it ? "Accesso…" : "Signing in…") : (it ? "Accedi" : "Sign in")} <I d={ic.arrow} size={14} color={T.navy} /></Btn>
              <div style={{ textAlign: "center", marginTop: 20, fontSize: 13, color: T.textSec }}>
                {it ? "Non hai un account?" : "Don't have an account?"}{" "}
                <span onClick={() => { setMode("register"); setError(""); }} style={{ color: T.accentDark, fontWeight: 700, cursor: "pointer" }}>{it ? "Crea un account →" : "Create an account →"}</span>
              </div>
            </>
          ) : (
            <>
              <h2 style={{ fontSize: 24, fontWeight: 800, color: T.navy, marginBottom: 4 }}>{it ? "Crea il tuo account" : "Create your account"}</h2>
              <p style={{ fontSize: 13, color: T.textSec, marginBottom: 24 }}>{it ? "Registra la tua azienda per iniziare a creare passaporti digitali." : "Register your company to start creating digital passports."}</p>
              <ErrorBox />
              {inp(it ? "Nome e cognome" : "Full name", "name")}
              {inp(it ? "Azienda" : "Company", "company")}
              {inp(it ? "Email aziendale" : "Business email", "email", "email", "mario.rossi@azienda.it")}
              {inp("Password", "password", "password", it ? "Almeno 8 caratteri" : "At least 8 characters")}
              <Btn primary onClick={doRegister} style={{ width: "100%", opacity: busy ? 0.6 : 1 }}>{busy ? (it ? "Creazione…" : "Creating…") : (it ? "Crea account" : "Create account")} <I d={ic.arrow} size={14} color={T.navy} /></Btn>
              <div style={{ textAlign: "center", marginTop: 16, fontSize: 13, color: T.textSec }}>
                {it ? "Hai già un account?" : "Already have an account?"}{" "}
                <span onClick={() => { setMode("login"); setError(""); }} style={{ color: T.accentDark, fontWeight: 700, cursor: "pointer" }}>{it ? "Accedi" : "Sign in"}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── ONBOARDING ──────────────────────────────────────────
function OnboardingUpload({ onNavigate, L, onExtracted, presetType = null }) {
  const _ = k => t(k, L?.lang);
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState("");
  const [detectedInfo, setDetectedInfo] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [dppType, setDppType] = useState(presetType); // null | "model" | "batch" | "item"
  const fileInputRef = useRef(null);

  const formatSize = (bytes) => bytes < 1024*1024 ? (bytes/1024).toFixed(0)+" KB" : (bytes/(1024*1024)).toFixed(1)+" MB";

  const handleFiles = (fileList) => {
    const supported = [".pdf",".jpg",".jpeg",".png",".tiff",".tif",".xlsx",".xls"];
    const valid = Array.from(fileList).filter(f => supported.some(ext => f.name.toLowerCase().endsWith(ext)));
    if (valid.length) setFiles(prev => [...prev, ...valid.map(f => ({ file: f, name: f.name, size: formatSize(f.size) }))]);
  };

  const removeFile = (idx) => setFiles(prev => prev.filter((_, i) => i !== idx));

  const start = async () => {
    setProcessing(true); setProgress(5); setError(null);
    setStatusMsg(L?.lang==="it" ? "Caricamento documenti..." : "Uploading documents...");

    const formData = new FormData();
    files.forEach(f => formData.append("files", f.file));
    if (websiteUrl.trim()) formData.append("website_url", websiteUrl.trim());
    if (dppType) formData.append("dpp_type", dppType);

    try {
      const res = await fetch("/api/extract", { method: "POST", credentials: "include", body: formData });
      const { job_id, error: uploadErr } = await res.json();
      if (!job_id) { setError(uploadErr || "Upload failed"); setProcessing(false); return; }

      const evtSource = new EventSource(`/api/jobs/${job_id}`);
      const it = L?.lang === "it";

      evtSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        setProgress(data.progress || 0);
        if (data.step === "classify") setStatusMsg(it ? `Classificazione documento ${data.doc_index||""}/${data.doc_total||""}...` : `Classifying document ${data.doc_index||""}/${data.doc_total||""}...`);
        else if (data.step === "extract") { setStatusMsg(it ? `Estrazione dati da ${data.detail||""}...` : `Extracting data from ${data.detail||""}...`); if (data.detail && !detectedInfo) setDetectedInfo(data.detail); }
        else if (data.step === "merge") setStatusMsg(it ? "Unione e riconciliazione dati..." : "Merging and reconciling data...");
        else if (data.step === "done" || data.status === "done") { setStatusMsg(it ? "Fatto!" : "Done!"); setProgress(100); }
        if (data.status === "error") { setError(data.error || "Extraction failed"); evtSource.close(); setProcessing(false); }
      };

      evtSource.addEventListener("result", (e) => {
        const result = JSON.parse(e.data);
        evtSource.close();
        if (onExtracted) onExtracted(result);
        setTimeout(() => onNavigate("app-edit"), 800);
      });

      evtSource.onerror = () => {
        evtSource.close();
        const poll = setInterval(async () => {
          try {
            const r = await fetch(`/api/jobs/${job_id}/result`, { credentials: "include" });
            const data = await r.json();
            if (data.passport) { clearInterval(poll); if (onExtracted) onExtracted(data); setProgress(100); setStatusMsg(it?"Fatto!":"Done!"); setTimeout(() => onNavigate("app-edit"), 800); }
            else if (data.error) { clearInterval(poll); setError(data.error); setProcessing(false); }
          } catch (_) {}
        }, 2000);
      };
    } catch (err) { setError(err.message); setProcessing(false); }
  };

  const it = L?.lang === "it";
  return (
    <div style={{ fontFamily: font, minHeight: "100vh", display: "flex" }}>
      <Sidebar activePage="onboard" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 48, background: T.bgSoft }}>
        <div style={{ maxWidth: 540, width: "100%", textAlign: "center" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 10, marginBottom: 20 }}><img src={LOGO_SRC} alt="DeePPy" style={{ height: 40, width: 40, objectFit: "cover", borderRadius: 10 }} /><span style={{ fontSize: 22, fontWeight: 800, color: T.textDark, letterSpacing: "-0.02em" }}>DeePPy</span></div>
          <div style={{ marginBottom: 6 }}><Badge>{it ? "BENVENUTO" : "WELCOME"}</Badge></div>
          <h1 style={{ fontSize: 26, fontWeight: 800, color: T.navy, marginBottom: 6 }}>{it ? "Crea un nuovo passaporto digitale" : "Create a new digital passport"}</h1>
          <p style={{ fontSize: 14, color: T.textSec, lineHeight: 1.6, marginBottom: 20 }}>{it ? "Seleziona il tipo di DPP e carica i documenti." : "Select the DPP type and upload your documents."}</p>
        {!processing ? (!dppType ? (
          /* DPP type selector */
          <div style={{ display: "flex", gap: 12, marginBottom: 28 }}>
            {[
              ["model", "DPP Model", it?"Prodotto-tipo. Dati tecnici, certificazioni, BOM.":"Product-type. Technical data, certifications, BOM.", T.navy, T.bgSoft, ic.box],
              ["batch", "DPP Batch", it?"Lotto produttivo. Eredita dal Model.":"Production batch. Inherits from Model.", T.accentDark||T.accent, T.accentSoft, ic.layers],
              ["item", "DPP Item", it?"Singolo prodotto. Eredita da Batch/Model.":"Individual product. Inherits from Batch/Model.", "#3B82F6", T.blueSoft||"#EFF6FF", ic.grid],
            ].map(([type, title, desc, color, bg, iconD]) => (
              <button key={type} onClick={()=>setDppType(type)} style={{ flex: 1, padding: "16px", borderRadius: 10, border: `2px solid ${T.border}`, background: T.bg, cursor: "pointer", textAlign: "center", fontFamily: font, transition: "all 0.15s" }} onMouseEnter={e=>{e.currentTarget.style.borderColor=color; e.currentTarget.style.background=bg+"30";}} onMouseLeave={e=>{e.currentTarget.style.borderColor=T.border; e.currentTarget.style.background=T.bg;}}>
                <div style={{ width: 36, height: 36, borderRadius: 9, background: bg, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 8px" }}><I d={iconD} size={16} color={color} /></div>
                <div style={{ fontSize: 14, fontWeight: 700, color: T.navy }}>{title}</div>
                <div style={{ fontSize: 11, color: T.textSec, marginTop: 4, lineHeight: 1.4 }}>{desc}</div>
              </button>
            ))}
          </div>
        ) : (<>
          {/* Type badge + change link */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 16 }}>
            <Badge color={dppType==="model"?T.textSec:dppType==="batch"?(T.accentDark||T.accent):"#3B82F6"} bg={dppType==="model"?T.bgSoft:dppType==="batch"?T.accentSoft:(T.blueSoft||"#EFF6FF")}>{dppType==="model"?"DPP Model":dppType==="batch"?"DPP Batch":"DPP Item"}</Badge>
            <button onClick={()=>setDppType(null)} style={{ background: "none", border: "none", color: T.textSec, fontSize: 11, cursor: "pointer", fontFamily: font }}>{it?"Cambia tipo →":"Change type →"}</button>
          </div>
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
            style={{ background: T.bg, borderRadius: 12, padding: files.length?22:44, border: `2px dashed ${dragOver?T.accent:files.length?T.accent:T.border}`, cursor: "pointer", marginBottom: 14, transition: "border .2s" }}
          >
            <input ref={fileInputRef} type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif,.xlsx,.xls" style={{ display: "none" }} onChange={(e) => { handleFiles(e.target.files); e.target.value = ""; }} />
            {files.length===0?(<><div style={{ marginBottom: 10 }}><I d={ic.upload} size={36} color={dragOver?T.accent:T.border} /></div><div style={{ fontSize: 15, fontWeight: 700, color: T.textDark }}>{it?"Trascina i file qui":"Drag files here"}</div><div style={{ fontSize: 12, color: T.textSec, marginTop: 4 }}>PDF, Excel, {it?"immagini":"images"} — Max 50MB</div></>):files.map((f,i)=>(<div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: i<files.length-1?`1px solid ${T.borderLight}`:"none", textAlign: "left" }}><div style={{ display: "flex", alignItems: "center", gap: 8 }}><I d={ic.file} size={16} color={T.accentDark} /><span style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{f.name} <span style={{ fontWeight: 400, color: T.textSec }}>({f.size})</span></span></div><button onClick={(e)=>{e.stopPropagation();removeFile(i);}} style={{ background:"none", border:"none", cursor:"pointer", padding:2 }}><I d={ic.x} size={14} color={T.textSec} /></button></div>))}
          </div>
          {/* Optional website URL */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, padding: "10px 14px", borderRadius: 10, border: `1px solid ${websiteUrl ? T.accent : T.border}`, background: T.bg, transition: "border-color 0.15s" }}>
            <I d={ic.globe} size={16} color={websiteUrl ? T.accent : T.textSec} />
            <input value={websiteUrl} onChange={e=>setWebsiteUrl(e.target.value)} placeholder={it?"Sito web (opzionale) — utile se i PDF non hanno tutti i contatti aziendali":"Website URL (optional) — useful when PDFs don't include full manufacturer contact info"} style={{ flex: 1, border: "none", outline: "none", fontSize: 13, background: "transparent", fontFamily: font, color: T.textDark }} />
          </div>
          {websiteUrl && <div style={{ fontSize: 11, color: T.accent, marginBottom: 14, display: "flex", alignItems: "center", gap: 4, justifyContent: "center" }}><I d={ic.check} size={11} color={T.accent} />{it?"Estrarremo contatti, descrizione azienda e info di base dal sito":"We'll extract company contact info and description from the website"}</div>}
          {(files.length>0||websiteUrl)&&<Btn primary onClick={start} style={{ width: "100%", fontSize: 15 }}>{it?"Crea la scheda del prodotto":"Generate Product Passport"} <I d={ic.arrow} size={16} color={T.navy} /></Btn>}
        </>)):(
          <div style={{ background: T.bg, borderRadius: 12, padding: 28, border: `1px solid ${T.border}`, textAlign: "left" }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: T.navy, marginBottom: 14 }}>{progress<100?(it?"Estrazione in corso...":"Extracting..."):(it?"Fatto!":"Done!")}</div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}><span style={{ fontSize: 12, color: T.textSec }}>{statusMsg}</span><span style={{ fontSize: 12, fontWeight: 700, color: T.accent }}>{Math.round(progress)}%</span></div>
            <div style={{ width: "100%", height: 5, borderRadius: 3, background: T.border }}><div style={{ width: `${progress}%`, height: "100%", borderRadius: 3, background: T.accent, transition: "width .3s" }} /></div>
            {detectedInfo&&progress>=30&&progress<100&&<div style={{ marginTop: 14, padding: 10, borderRadius: 6, background: T.accentSoft, fontSize: 12, color: T.accentDark, display: "flex", alignItems: "center", gap: 6 }}><I d={ic.check} size={14} color={T.accentDark} /> {it?"Documento in elaborazione:":"Processing document:"} <strong>{detectedInfo}</strong></div>}
            {error&&<div style={{ marginTop: 10, padding: "8px 12px", borderRadius: 6, background: T.redSoft||"#FEE2E2", fontSize: 12, color: T.red }}>{error}</div>}
          </div>
        )}
        <div style={{ marginTop: 20, fontSize: 12, color: T.textSec }}>{it ? "Non hai documenti?" : "No documents?"} <span style={{ color: T.accentDark, fontWeight: 600, cursor: "pointer" }} onClick={() => onNavigate("app-edit")}>{it ? "Salta e compila manualmente" : "Skip and fill manually"}</span></div>
      </div>
      </div>
    </div>
  );
}

// ─── COMPONENTI TAB (shared edit + published) ────────────
function ComponentiTab({ editMode, onNavigate, L, dppData }) {
  const _ = k => t(k, L?.lang);
  const it = L?.lang === "it";
  const _pp = dppData?.passport;
  const _mv = (m, f) => { const x = m?.[f]; return (x && typeof x === "object") ? x.value : x; };

  // Build the component list from the real Bill of Materials when available.
  const buildFromPassport = () => (_pp?.composition?.materials || []).map((m, i) => {
    const pct = _mv(m, "percentage");
    const qty = _mv(m, "quantity_per_product");
    const unit = _mv(m, "unit");
    const origin = _mv(m, "origin");
    const rec = _mv(m, "recyclable");
    const parts = [];
    if (pct != null && pct !== "") parts.push(`${pct}%`);
    if (qty != null && qty !== "") parts.push(`${qty}${unit ? " " + unit : ""}`);
    if (origin) parts.push((it ? "Origine " : "Origin ") + origin);
    if (rec) parts.push(String(rec));
    const sup = (m.suppliers && m.suppliers[0]) || null;
    const supName = sup ? _mv(sup, "name") : null;
    const descField = m.description;
    return {
      id: _mv(m, "id_code") || m.material_id || ("mat" + i),
      linked: false,
      genericName: _mv(m, "description") || (it ? "Materiale" : "Material"),
      detail: parts.join(" — ") || null,
      source: supName && supName !== "-" ? supName : "EPD / BoM",
      conf: (descField && typeof descField === "object" && descField.confidence) || "high",
    };
  });

  const demoComponents = [
    { id: "m1", linked: false, genericName: "Extruded Polystyrene", detail: "92% — 2.3 kg/m² — Origine EU — Riciclabile", source: "EPD, Tabella 2", conf: "high" },
    { id: "m2", linked: false, genericName: "Flame Retardant Additives", detail: "5% — 0.12 kg/m² — Origine EU — Non riciclabile", source: "EPD, Tabella 2", conf: "high" },
    { id: "m3", linked: false, genericName: "Other components", detail: "3% — 0.07 kg/m² — Origine mista", source: "EPD", conf: "high" },
  ];

  const [components, setComponents] = useState(_pp?.composition?.materials?.length ? buildFromPassport() : demoComponents);
  // Re-sync when real passport data arrives (e.g. after detail load).
  useEffect(() => {
    if (_pp?.composition?.materials?.length) setComponents(buildFromPassport());
  }, [dppData]);
  const [searchFor, setSearchFor] = useState(null);
  const [catSearch, setCatSearch] = useState("");
  const [inviteFor, setInviteFor] = useState(null);
  const [editingId, setEditingId] = useState(null);

  // Catalog rows for the "link to a published product" picker. Live data —
  // map server fields onto the {name, cat, prod, co2} shape this code expects.
  const [catalogItems, setCatalogItems] = useState([]);
  useEffect(() => {
    fetch("/api/catalog", { credentials: "include" })
      .then(r => r.ok ? r.json() : [])
      .then(rows => {
        if (!Array.isArray(rows)) return;
        setCatalogItems(rows.map(r => ({
          id: r.id,
          name: r.name || "—",
          cat: r.family_code || "—",
          prod: r.manufacturer || r.company_name || "—",
          co2: r.kpis?.gwp_total != null ? String(r.kpis.gwp_total) : "",
        })));
      })
      .catch(() => {});
  }, []);

  const available = catalogItems.filter(c => !components.find(x => x.linked && x.name === c.name) && (!catSearch || c.name.toLowerCase().includes(catSearch.toLowerCase()) || c.cat.toLowerCase().includes(catSearch.toLowerCase())));

  const linkComp = (compId, item) => {
    setComponents(p => p.map(c => c.id === compId ? { ...c, linked: true, name: item.name, cat: item.cat, prod: item.prod, co2: item.co2, owner: item.prod, updated: "Today" } : c));
    setSearchFor(null); setCatSearch("");
  };
  const removeComp = (id) => setComponents(p => p.filter(x => x.id !== id));
  const unlinkComp = (id) => setComponents(p => p.map(c => c.id === id ? { ...c, linked: false, genericName: c.name, name: undefined, prod: undefined, co2: undefined, owner: undefined } : c));
  const [newName, setNewName] = useState("");
  const addManual = () => {
    if (!newName.trim()) return;
    setComponents(p => [...p, { id: "c" + Date.now(), linked: false, genericName: newName.trim(), source: "Manually added" }]);
    setNewName(""); setShowAdd(false);
  };
  const [showAdd, setShowAdd] = useState(false);

  return (
    <div>
      <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden", marginBottom: 16 }}>
        <div style={{ padding: "14px 18px", borderBottom: `1px solid ${T.borderLight}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <I d={ic.layers} size={16} color={T.accentDark} />
            <span style={{ fontSize: 15, fontWeight: 700, color: T.textDark }}>{_("productStructure")}</span>
            <Badge color={T.accentDark} bg={T.accentSoft}>{components.filter(c=>c.linked).length}/{components.length} collegati</Badge>
          </div>
        </div>

        <div style={{ padding: "16px 18px" }}>
          {/* Root */}
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "12px 14px", marginBottom: 4, borderRadius: 8, background: T.navyLight, border: `1px solid ${T.navyMid}` }}>
            <div style={{ width: 36, height: 36, borderRadius: 8, background: T.accent+"30", display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.box} size={16} color={T.accent} /></div>
            <div style={{ flex: 1 }}><div style={{ fontSize: 14, fontWeight: 700, color: T.text }}>{_pp?.overview?.product_info?.product_name?.value || "XPS Insulation Panel 100mm"}</div><div style={{ fontSize: 11, color: T.textMuted }}>{_("mainProduct")}</div></div>
            <Badge color={T.accent} bg={T.accent+"30"}><I d={ic.shield} size={9} color={T.accent} /> Tuo</Badge>
          </div>

          {/* Components */}
          {components.map((c, i) => {
            const isEd = editingId === c.id;
            const confColor = c.conf === "high" ? T.accent : c.conf === "medium" ? T.amber : T.red;
            return (
            <div key={c.id}>
              <div style={{ width: 2, height: 10, background: T.border, marginLeft: 32 }} />

              {c.linked ? (
                <div style={{ marginLeft: 20, borderRadius: 8, background: T.bg, border: `1px solid ${T.border}`, overflow: "hidden" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 14px" }}>
                    <div style={{ width: 32, height: 32, borderRadius: 6, background: T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.box} size={14} color={T.accentDark} /></div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div onClick={() => onNavigate && onNavigate("app")} style={{ fontSize: 13, fontWeight: 700, color: T.accentDark, cursor: "pointer", textDecoration: "underline", textDecorationColor: T.accentSoft, textUnderlineOffset: 2 }} title="Open DPP for this component">{c.name}</div>
                      <div style={{ fontSize: 11, color: T.textSec, display: "flex", alignItems: "center", gap: 8 }}><span style={{ display: "flex", alignItems: "center", gap: 3 }}><I d={ic.factory} size={10} color={T.textSec} />{c.prod}</span><span>CO₂: {c.co2} kg</span></div>
                    </div>
                    <Conf c={c.conf || "high"} />
                    <Badge color={T.textSec} bg={T.bgSoft}><I d={ic.shield} size={9} color={T.textSec} /> {c.owner}</Badge>
                    {editMode && <button onClick={() => unlinkComp(c.id)} title="Unlink" style={{ background: "none", border: "none", cursor: "pointer", padding: 2 }}><I d={ic.x} size={14} color={T.textSec} /></button>}
                  </div>
                  {c.source && <div style={{ padding: "0 14px 8px 54px", fontSize: 10, color: T.textSec, display: "flex", alignItems: "center", gap: 3 }}><I d={ic.file} size={10} color={T.textSec} /> {_("source")}: {c.source}</div>}
                </div>
              ) : (
                <div style={{ marginLeft: 20 }}>
                  <div style={{ borderRadius: 8, background: T.bgSoft, border: `1px solid ${T.border}`, overflow: "hidden" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 14px" }}>
                      <div style={{ width: 32, height: 32, borderRadius: 6, background: T.bg, border: `1px solid ${T.border}`, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.box} size={14} color={T.textSec} /></div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {editMode && isEd ? (
                          <input autoFocus defaultValue={c.genericName} onBlur={e => { setComponents(p => p.map(x => x.id === c.id ? { ...x, genericName: e.target.value } : x)); setEditingId(null); }} style={{ width: "100%", border: "none", outline: "none", fontSize: 13, fontWeight: 700, color: T.textDark, background: "transparent", fontFamily: font }} />
                        ) : (
                          <div onClick={() => editMode && setEditingId(c.id)} style={{ fontSize: 13, fontWeight: 700, color: T.textDark, cursor: editMode ? "text" : "default" }}>{c.genericName}</div>
                        )}
                        {c.detail && (
                          editMode && isEd ? (
                            <input defaultValue={c.detail} onBlur={e => setComponents(p => p.map(x => x.id === c.id ? { ...x, detail: e.target.value } : x))} style={{ width: "100%", border: "none", outline: "none", fontSize: 11, color: T.textSec, background: "transparent", fontFamily: font, marginTop: 2 }} />
                          ) : (
                            <div onClick={() => editMode && setEditingId(c.id)} style={{ fontSize: 11, color: T.textSec, cursor: editMode ? "text" : "default" }}>{c.detail}</div>
                          )
                        )}
                        {!c.detail && <div style={{ fontSize: 11, color: T.textSec }}>{c.source || "Component"}</div>}
                      </div>
                      <Conf c={c.conf || "medium"} />
                      {editMode && (
                        <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                          <Btn small onClick={() => { setSearchFor(c.id); setInviteFor(null); }} style={{ padding: "5px 12px", fontSize: 11 }}><I d={ic.search} size={11} color={T.textSec} /> Catalogo</Btn>
                          <Btn small onClick={() => { setInviteFor(c.id); setSearchFor(null); }} style={{ padding: "5px 12px", fontSize: 11 }}><I d={ic.users} size={11} color={T.textSec} /> Invita</Btn>
                        </div>
                      )}
                      {editMode && <button onClick={() => removeComp(c.id)} title="Remove" style={{ background: "none", border: "none", cursor: "pointer", padding: 2 }}><I d={ic.x} size={14} color={T.textSec} /></button>}
                    </div>
                    {c.detail && c.source && <div style={{ padding: "0 14px 8px 54px", fontSize: 10, color: T.textSec, display: "flex", alignItems: "center", gap: 3 }}><I d={ic.file} size={10} color={T.textSec} /> {_("source")}: {c.source}</div>}
                  </div>

                  {/* Inline search for this component */}
                  {searchFor === c.id && (
                    <div style={{ marginTop: 6, padding: "12px 14px", borderRadius: 8, border: `2px solid ${T.accent}`, background: T.bg }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                        <I d={ic.search} size={14} color={T.textSec} />
                        <input autoFocus value={catSearch} onChange={e => setCatSearch(e.target.value)} placeholder="Search catalog…" style={{ flex: 1, border: "none", outline: "none", fontSize: 12, background: "transparent", fontFamily: font }} />
                        <button onClick={() => setSearchFor(null)} style={{ background: "none", border: "none", cursor: "pointer" }}><I d={ic.x} size={14} color={T.textSec} /></button>
                      </div>
                      <div style={{ maxHeight: 180, overflowY: "auto" }}>
                        {available.map((item, j) => (
                          <div key={j} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "7px 10px", borderRadius: 6, marginBottom: 3, background: T.bgSoft }}>
                            <div><div style={{ fontSize: 12, fontWeight: 600, color: T.textDark }}>{item.name}</div><div style={{ fontSize: 10, color: T.textSec }}>{item.prod} — {item.cat}</div></div>
                            <Btn small primary onClick={() => linkComp(c.id, item)} style={{ padding: "3px 10px", fontSize: 10 }}>Collega</Btn>
                          </div>
                        ))}
                        {available.length === 0 && <div style={{ fontSize: 11, color: T.textSec, textAlign: "center", padding: 8 }}>Nessun risultato</div>}
                      </div>
                    </div>
                  )}

                  {/* Inline invite for this component */}
                  {inviteFor === c.id && (
                    <div style={{ marginTop: 6, padding: "12px 14px", borderRadius: 8, border: `1px solid ${T.border}`, background: T.bg }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: T.textDark, marginBottom: 6 }}>Invita il fornitore di "{c.genericName}"</div>
                      <div style={{ display: "flex", gap: 6 }}>
                        <input placeholder="Supplier email" style={{ flex: 1, padding: "6px 10px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 11, outline: "none", fontFamily: font }} />
                        <Btn small primary onClick={() => setInviteFor(null)} style={{ padding: "5px 12px", fontSize: 11 }}>Invia</Btn>
                      </div>
                      <div style={{ marginTop: 6 }}><Badge color={T.textSec} bg={T.bgSoft}>COMING SOON</Badge></div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );})}

          {/* Add component manually */}
          {editMode && !showAdd && (
            <div style={{ marginTop: 8 }}>
              <div style={{ width: 2, height: 10, background: T.border, marginLeft: 32 }} />
              <button onClick={() => setShowAdd(true)} style={{ marginLeft: 20, display: "flex", alignItems: "center", gap: 6, padding: "9px 14px", borderRadius: 8, border: `1px dashed ${T.border}`, background: "transparent", cursor: "pointer", fontFamily: font, fontSize: 13, color: T.textSec, width: "calc(100% - 20px)" }}>
                <I d={ic.plus} size={14} color={T.textSec} /> Aggiungi componente
              </button>
            </div>
          )}
          {editMode && showAdd && (
            <div style={{ marginTop: 8 }}>
              <div style={{ width: 2, height: 10, background: T.border, marginLeft: 32 }} />
              <div style={{ marginLeft: 20, display: "flex", gap: 8, alignItems: "center", padding: "8px 14px", borderRadius: 8, border: `1px solid ${T.accent}`, background: T.bg }}>
                <I d={ic.plus} size={14} color={T.accentDark} />
                <input autoFocus value={newName} onChange={e => setNewName(e.target.value)} onKeyDown={e => e.key === "Enter" && addManual()} placeholder="Nome componente (es. Guarnizione EPDM)" style={{ flex: 1, border: "none", outline: "none", fontSize: 13, background: "transparent", fontFamily: font }} />
                <Btn small primary onClick={addManual} style={{ padding: "4px 12px", fontSize: 11 }}>Aggiungi</Btn>
                <button onClick={() => { setShowAdd(false); setNewName(""); }} style={{ background: "none", border: "none", cursor: "pointer" }}><I d={ic.x} size={14} color={T.textSec} /></button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Responsibility */}
      {components.filter(c => c.linked).length > 0 && (
      <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, padding: "14px 18px" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: T.textDark, marginBottom: 6, display: "flex", alignItems: "center", gap: 6 }}><I d={ic.shield} size={14} color={T.accentDark} /> Responsabilità distribuita</div>
        <div style={{ fontSize: 12, color: T.textSec, lineHeight: 1.6 }}>Ogni componente collegato mantiene il proprietario originale come responsabile. Gli aggiornamenti si propagano automaticamente.</div>
        <div style={{ display: "flex", gap: 10, marginTop: 8, flexWrap: "wrap" }}>
          {components.filter(c => c.linked).map(c => (
            <div key={c.id} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: T.textSec }}><span style={{ width: 6, height: 6, borderRadius: "50%", background: T.accent }} />{c.owner}</div>
          ))}
          {components.filter(c => !c.linked).length > 0 && (
            <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: T.textSec }}><span style={{ width: 6, height: 6, borderRadius: "50%", background: T.border }} />{components.filter(c => !c.linked).length} senza DPP associato</div>
          )}
        </div>
      </div>
      )}
    </div>
  );
}

// ─── LIFECYCLE TAB ──────────────────────────────────────
function LifecycleTab({ L, dppData }) {
  const _ = k => t(k, L?.lang);
  const it = L?.lang === "it";
  const [activePhase, setActivePhase] = useState("a1");
  const _pp = dppData?.passport;
  const hasAI = !!_pp;
  const stages = [
    { group: "Production", color: T.accent, phases: [
      { key: "a1", label: "A1", title: "Raw Materials", iconD: ic.layers },
      { key: "a2", label: "A2", title: "Transport", iconD: ic.truck },
      { key: "a3", label: "A3", title: "Manufacturing", iconD: ic.factory },
    ]},
    { group: "Distribution", color: "#3B82F6", phases: [
      { key: "a4", label: "A4", title: "Transport", iconD: ic.truck },
      { key: "a5", label: "A5", title: "Installation", iconD: ic.tool },
    ]},
    { group: "Use", color: "#8B5CF6", phases: [
      { key: "b1", label: "B1", title: "Use", iconD: ic.home },
      { key: "b2", label: "B2-B3", title: "Maintenance", iconD: ic.tool },
      { key: "b4", label: "B4-B5", title: "Replacement", iconD: ic.recycle },
      { key: "b6", label: "B6-B7", title: "Energy/Water", iconD: ic.energy },
    ]},
    { group: "End of Life", color: "#F59E0B", phases: [
      { key: "c1", label: "C1", title: "Deconstruction", iconD: ic.tool },
      { key: "c2", label: "C2", title: "Transport", iconD: ic.truck },
      { key: "c3", label: "C3-C4", title: "Processing", iconD: ic.recycle },
    ]},
  ];
  const demoPhaseContent = {
    a1: { title: "A1 — Raw Material Supply", source: "EPD-XPS100-2025.pdf, Sez. LCA", fields: [
      { l: "Polystyrene (granule)", v: "92% — Origine EU", c: "high" },
      { l: "Flame retardant additives", v: "5% — HBCD-free, polimerico", c: "high" },
      { l: "Blowing agent (CO₂/HFC)", v: "3% — CO₂-based", c: "high" },
      { l: "GWP A1", v: "3.21 kg CO₂eq/FU", c: "high" },
      { l: "Material origin", v: "Virgin (100%)", c: "medium" },
    ]},
    a2: { title: "A2 — Raw Material Transport", source: "EPD-XPS100-2025.pdf", fields: [
      { l: "Transport type", v: "Road (truck 16-32t)", c: "high" },
      { l: "Average distance", v: "320 km", c: "medium" },
      { l: "GWP A2", v: "0.18 kg CO₂eq/FU", c: "high" },
    ]},
    a3: { title: "A3 — Manufacturing", source: "EPD-XPS100-2025.pdf", hasDiagram: true, fields: [
      { l: "Manufacturing process", v: "Continuous extrusion → cutting → packaging", c: "high" },
      { l: "Production Site", v: "Novara Plant, Via Industria 8", c: "medium" },
      { l: "Energy consumed", v: "12.4 MJ/FU", c: "high" },
      { l: "GWP A3", v: "1.05 kg CO₂eq/FU", c: "high" },
      { l: "Production waste", v: "< 2% (internally reprocessed)", c: "medium" },
    ]},
    a4: { title: "A4 — Transport to Site", source: "EPD-XPS100-2025.pdf", fields: [
      { l: "Transport type", v: "Road (truck 16-32t)", c: "high" },
      { l: "Scenario distance", v: "100 km", c: "medium" },
      { l: "Transport company", v: "", c: "low" },
      { l: "Destination", v: "", c: "low" },
      { l: "GWP A4", v: "0.06 kg CO₂eq/FU", c: "high" },
    ]},
    a5: { title: "A5 — Construction & Installation", source: "Non disponibile", fields: [
      { l: "Installation method statement", v: "", c: "low" },
      { l: "Installation date", v: "", c: "low" },
      { l: "Installation company", v: "", c: "low" },
      { l: "GWP A5", v: "0.02 kg CO₂eq/FU", c: "high" },
    ]},
    b1: { title: "B1 — Intended Use", source: "Technical Data Sheet", fields: [
      { l: "Intended use", v: "Thermal insulation for walls, roofs, floors", c: "high" },
      { l: "Reference Service Life (RSL)", v: "50 years", c: "high" },
    ]},
    b2: { title: "B2-B3 — Maintenance & Repair", source: "Non disponibile", fields: [
      { l: "Maintenance method statement", v: "", c: "low" },
      { l: "Maintenance frequency", v: "None (if protected)", c: "medium" },
      { l: "Maintenance company", v: "", c: "low" },
    ]},
    b4: { title: "B4-B5 — Replacement & Refurbishment", source: "Non disponibile", fields: [
      { l: "Replacement method statement", v: "", c: "low" },
      { l: "Expected replacement cycles", v: "0 (service life = building)", c: "medium" },
    ]},
    b6: { title: "B6-B7 — Operational Energy & Water", source: "Non disponibile", fields: [
      { l: "Operational energy consumption", v: "N/A (passive product)", c: "high" },
      { l: "Operational water consumption", v: "N/A", c: "high" },
    ]},
    c1: { title: "C1 — Deconstruction & Demolition", source: "Non disponibile", fields: [
      { l: "Deconstruction method statement", v: "", c: "low" },
      { l: "Deconstruction company", v: "", c: "low" },
      { l: "GWP C1", v: "0.01 kg CO₂eq/FU", c: "high" },
    ]},
    c2: { title: "C2 — End of Life Transport", source: "EPD-XPS100-2025.pdf", fields: [
      { l: "Transport type", v: "Road", c: "high" },
      { l: "Distance to facility", v: "50 km (scenario)", c: "medium" },
      { l: "GWP C2", v: "0.03 kg CO₂eq/FU", c: "high" },
    ]},
    c3: { title: "C3-C4 — Waste Processing & Disposal", source: "EPD-XPS100-2025.pdf", fields: [
      { l: "End of Life instructions", v: "Mechanical recycling or energy recovery", c: "high" },
      { l: "Recyclability rate", v: "15% (scenario EPD)", c: "medium" },
      { l: "GWP C3", v: "0.15 kg CO₂eq/FU", c: "high" },
      { l: "GWP C4", v: "0.08 kg CO₂eq/FU", c: "high" },
    ]},
  };

  // Build phase content from the real EPD lifecycle data in the passport.
  const buildRealPhaseContent = () => {
    const lc = (_pp && typeof _pp.lifecycle === "object" && _pp.lifecycle) || {};
    // stages can come in as null, an object, or a missing key — coerce to array.
    const stagesArr = Array.isArray(lc.stages) ? lc.stages : [];
    // norm() used to crash with "code.replace is not a function" when stage_code
    // came back wrapped as `{ value: "A1-A3", confidence }` instead of a plain
    // string (older passports). String() coerces either shape safely.
    const norm = (code) => {
      if (code == null) return "";
      const s = typeof code === "object" ? (code.value ?? "") : code;
      return String(s).replace(/[\s-]/g, "").toUpperCase();
    };
    const val = (obj, key) => { const x = obj?.[key]; return (x && typeof x === "object") ? x.value : x; };
    const indicatorRows = [
      ["GWP total", "gwp_total", "kg CO₂eq"], ["GWP fossil", "gwp_fossil", "kg CO₂eq"],
      ["GWP biogenic", "gwp_biogenic", "kg CO₂eq"], ["ODP", "odp", "kg CFC-11eq"],
      ["AP", "ap", "mol H⁺eq"], ["EP freshwater", "ep_freshwater", "kg Peq"],
      ["EP marine", "ep_marine", "kg Neq"], ["POCP", "pocp", "kg NMVOCeq"],
      ["ADP minerals", "adp_minerals", "kg Sbeq"], ["ADP fossil", "adp_fossil", "MJ"],
      ["WDP", "wdp", "m³"],
    ];
    const indicators = (s) => !s ? [] : indicatorRows
      .map(([l, key, unit]) => { const v = val(s, key); return (v == null || v === "") ? null : { l, v: `${v} ${unit}`, c: "high" }; })
      .filter(Boolean);
    const map = { a1:"A1", a2:"A2", a3:"A3", a4:"A4", a5:"A5", b1:"B1", b2:"B2", b4:"B4", b6:"B6", c1:"C1", c2:"C2", c3:"C3" };
    const content = {};
    for (const [key, label] of Object.entries(map)) {
      const s = stagesArr.find(st => norm(st.stage_code).includes(label));
      content[key] = { title: label, source: s ? "EPD" : "Not available", fields: indicators(s) };
    }
    // Enrich A3 with manufacturing details (process, year, energy, water).
    const a3 = (typeof lc.a3_manufacturing === "object" && lc.a3_manufacturing) || {};
    const extra = [];
    if (val(a3, "process_description")) extra.push({ l: it?"Processo produttivo":"Manufacturing process", v: val(a3, "process_description"), c: "high" });
    if (val(a3, "reference_year")) extra.push({ l: it?"Anno di riferimento":"Reference year", v: String(val(a3, "reference_year")), c: "medium" });
    const en = (typeof a3.energy === "object" && a3.energy) || {};
    if (val(en, "energy_electrical")) extra.push({ l: it?"Energia elettrica":"Electrical energy", v: `${val(en, "energy_electrical")} kWh`, c: "high" });
    if (val(en, "energy_thermal")) extra.push({ l: it?"Energia termica":"Thermal energy", v: `${val(en, "energy_thermal")} Sm³`, c: "high" });
    if (val(a3, "water_use")) extra.push({ l: it?"Consumo acqua":"Water use", v: `${val(a3, "water_use")} m³`, c: "high" });
    if (val(a3, "packaging")) extra.push({ l: it?"Imballaggio":"Packaging", v: val(a3, "packaging"), c: "medium" });
    const prevA3 = content.a3 || { title: "A3", source: "Not available", fields: [] };
    content.a3 = { title: "A3", source: prevA3.source, fields: [...extra, ...(prevA3.fields || [])] };
    return content;
  };

  // buildRealPhaseContent can blow up on unexpected passport shapes; fall
  // back to an empty skeleton so the tab still renders instead of taking the
  // whole product page down.
  let phaseContent;
  try {
    phaseContent = hasAI ? buildRealPhaseContent() : demoPhaseContent;
  } catch (err) {
    console.error("LifecycleTab: failed to build phase content", err);
    phaseContent = {};
  }
  const active = (phaseContent && phaseContent[activePhase]) || { title: activePhase.toUpperCase(), source: "Not available", fields: [] };
  // Defensive: ensure fields is always an array we can .map/.some over.
  if (!Array.isArray(active.fields)) active.fields = [];
  return (
    <div>
      {/* Timeline */}
      <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, padding: "16px 20px", marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 2 }}>
          {stages.map((st, si) => (
            <div key={si} style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: st.color, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6, textAlign: "center" }}>{st.group}</div>
              <div style={{ display: "flex", gap: 2 }}>
                {st.phases.map((ph) => {
                  const isActive = activePhase === ph.key;
                  const hasData = Array.isArray(phaseContent?.[ph.key]?.fields)
                    && phaseContent[ph.key].fields.some(f => f && f.v);
                  return (
                    <button key={ph.key} onClick={() => setActivePhase(ph.key)} style={{
                      flex: 1, padding: "8px 2px", borderRadius: 6, border: isActive ? `2px solid ${st.color}` : `1px solid ${T.border}`,
                      background: isActive ? st.color + "15" : hasData ? T.bg : T.bgSoft, cursor: "pointer", fontFamily: font, textAlign: "center",
                      display: "flex", flexDirection: "column", alignItems: "center", gap: 3,
                    }}>
                      <I d={ph.iconD} size={13} color={isActive ? st.color : hasData ? T.textDark : T.textSec} />
                      <div style={{ fontSize: 10, fontWeight: 800, color: isActive ? st.color : T.textDark }}>{ph.label}</div>
                      <div style={{ fontSize: 8, color: isActive ? st.color : T.textSec, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: "100%" }}>{ph.title}</div>
                      {!hasData && <div style={{ width: 4, height: 4, borderRadius: 2, background: T.border }} />}
                    </button>
                  );
                })}
              </div>
              {si < stages.length - 1 && <div style={{ display: "none" }} />}
            </div>
          ))}
        </div>
      </div>
      {/* Phase detail */}
      <ColSec title={active.title} iconD={ic.clock} badge={
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          {active.source !== "Not available" && <button style={{ background: "none", border: `1px solid ${T.accent}`, borderRadius: 5, padding: "3px 8px", fontSize: 10, fontWeight: 600, color: T.accentDark, cursor: "pointer", fontFamily: font, display: "flex", alignItems: "center", gap: 3 }}><I d={ic.file} size={10} color={T.accentDark} />{active.source}</button>}
          {active.source === "Not available" && <Badge color={T.textSec} bg={T.bgSoft}>Data not available</Badge>}
        </div>
      }>
        {/* A3 Manufacturing Process Diagram */}
        {active.hasDiagram && (
          <div style={{ marginBottom: 16, padding: 16, borderRadius: 8, background: T.bgSoft, border: `1px solid ${T.border}` }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 10, display: "flex", alignItems: "center", gap: 4 }}><I d={ic.factory} size={12} color={T.textSec} /> {L?.lang==="it"?"Flusso Processo Produttivo":"Manufacturing Process Flow"} <span style={{ marginLeft: "auto", fontSize: 10, color: T.accentDark, cursor: "pointer", textDecoration: "underline" }}>{_("source")}: EPD-XPS100-2025.pdf, p.8</span></div>
            <svg viewBox="0 0 600 80" style={{ width: "100%", height: 70 }}>
              {[
                { x: 10, label: "Raw\nMaterials", sub: "Polystyrene\ngranule", icon: ic.layers },
                { x: 130, label: "Mixing &\nAdditives", sub: "Flame retardant\n+ blowing agent", icon: ic.tool },
                { x: 250, label: "Continuous\nExtrusion", sub: "220°C\nco-extrusion", icon: ic.factory },
                { x: 370, label: "Cooling &\nCutting", sub: "Standard dims\n1250×600mm", icon: ic.tool },
                { x: 490, label: "Packaging &\nQC", sub: "FPC cert.\n0123-CPR", icon: ic.check },
              ].map((step, i) => (
                <g key={i}>
                  {i > 0 && <path d={`M${step.x - 18} 28 L${step.x - 4} 28`} stroke={T.accent} strokeWidth={2} markerEnd="none" />}
                  {i > 0 && <polygon points={`${step.x - 6},24 ${step.x - 6},32 ${step.x},28`} fill={T.accent} />}
                  <rect x={step.x} y={8} width={95} height={40} rx={8} fill={T.bg} stroke={T.accent} strokeWidth={1.5} />
                  <text x={step.x + 48} y={24} textAnchor="middle" fontSize={9} fontWeight="700" fill={T.textDark} fontFamily={font}>{step.label.split("\n")[0]}</text>
                  <text x={step.x + 48} y={34} textAnchor="middle" fontSize={9} fontWeight="700" fill={T.textDark} fontFamily={font}>{step.label.split("\n")[1]}</text>
                  <text x={step.x + 48} y={58} textAnchor="middle" fontSize={7.5} fill={T.textSec} fontFamily={font}>{step.sub.split("\n")[0]}</text>
                  <text x={step.x + 48} y={67} textAnchor="middle" fontSize={7.5} fill={T.textSec} fontFamily={font}>{step.sub.split("\n")[1]}</text>
                </g>
              ))}
            </svg>
          </div>
        )}
        {active.fields.map((f, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: i < active.fields.length - 1 ? `1px solid ${T.borderLight}` : "none" }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 11, color: T.textSec, marginBottom: 1 }}>{f.l}</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: f.v ? T.textDark : T.textSec, fontStyle: f.v ? "normal" : "italic" }}>{f.v || "Not filled in"}</div>
            </div>
            <Conf c={f.c} onClick={f.c === "medium" ? () => {} : undefined} />
          </div>
        ))}
      </ColSec>
    </div>
  );
}

// ─── DPP DATA HELPER ─────────────────────────────────────
function _ef(passport, path) {
  if (!passport) return {};
  const parts = path.split(".");
  let obj = passport;
  for (const p of parts) { obj = obj?.[p]; if (obj === undefined || obj === null) return {}; }
  if (typeof obj !== "object" || !("value" in obj)) return {};
  const src = obj.source;
  const srcStr = src ? (typeof src === "string" ? src : `${src.document_name || ""}${src.page ? `, p. ${src.page}` : ""}`) : null;
  return {
    v: obj.value != null ? String(obj.value) : null,
    c: obj.confidence || "low",
    s: srcStr,
    n: obj.note || null,
    path,
  };
}

// ─── APP EDIT VIEW (DRAFT) ───────────────────────────────
function AppEditView({ onNavigate, L, dppData, product, onAddProjectDPP, onSave }) {
  const _ = k => t(k, L?.lang);
  const [tab, setTab] = useState("panoramica");
  const [chatOpen, setChatOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [updateFiles, setUpdateFiles] = useState([]);
  const [updateProgress, setUpdateProgress] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  // Field edits captured by path, e.g. { "overview.product_info.weight": "13 kg" }
  const [edits, setEdits] = useState({});

  // Persist edits: deep-merge into the passport and PATCH via the parent.
  const handleSave = async () => {
    const paths = Object.keys(edits);
    if (onSave && product?.id && dppData?.passport && paths.length) {
      setSaving(true);
      const next = JSON.parse(JSON.stringify(dppData.passport));
      for (const path of paths) {
        const parts = path.split(".");
        let obj = next;
        for (let i = 0; i < parts.length - 1; i++) obj = obj?.[parts[i]];
        const leaf = parts[parts.length - 1];
        if (obj && obj[leaf] && typeof obj[leaf] === "object") {
          obj[leaf].value = edits[path];
          obj[leaf].confidence = "high";   // user-edited → high confidence
        }
      }
      await onSave(product.id, next, "Manual edit");
      setEdits({});
      setSaving(false);
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  // Project DPP state
  const [projBatch, setProjBatch] = useState("");
  const [projSite, setProjSite] = useState("");
  const [projRef, setProjRef] = useState("");
  const [projDims, setProjDims] = useState("");
  const [projWeight, setProjWeight] = useState("");
  const [projNotes, setProjNotes] = useState("");
  const [projCreated, setProjCreated] = useState(false);

  // AI data resolution
  const pp = dppData?.passport;
  const stats = dppData?.stats;
  const d = (path) => _ef(pp, path);
  const hasAI = !!pp;
  const initCompleteness = stats?.completeness ?? 87;
  const [completeness, setCompleteness] = useState(initCompleteness);
  useEffect(() => { if (stats?.completeness != null) setCompleteness(Math.round(stats.completeness)); }, [stats?.completeness]);
  const highCount = stats?.confidence?.high ?? (hasAI ? 0 : 14);
  const medCount = stats?.confidence?.medium ?? (hasAI ? 0 : 3);
  const lowCount = stats?.confidence?.low ?? (hasAI ? 0 : 1);
  // Required-field completion context (completion % is measured over mandatory fields)
  const reqFilled = stats?.required_filled;
  const reqTotal = stats?.required_total;
  const missingReq = stats?.missing_required || [];
  // All-fields completion (mandatory + optional) + a toggle to switch the view.
  const overallPct = stats?.overall_completeness ?? null;
  const allFilled = stats?.fields_filled;
  const allTotal = stats?.total_fields;
  // Recall vs an attached expert "expected results" file.
  const [recallState, setRecallState] = useState(null);
  useEffect(() => { if (stats?.recall) setRecallState(stats.recall); }, [stats?.recall]);
  const evalInputRef = useRef(null);
  const uploadEval = async (fileObj) => {
    if (!fileObj || !product?.id) return;
    const fd = new FormData(); fd.append("file", fileObj);
    try {
      const res = await fetch(`/api/products/${product.id}/eval-reference`, { method: "POST", credentials: "include", body: fd });
      const d = await res.json();
      if (res.ok && d.recall) { setRecallState(d.recall); setComplMode("recall"); }
    } catch { /* ignore */ }
  };

  const [complMode, setComplMode] = useState("required"); // "required" | "all" | "recall"
  const displayedPct = complMode === "recall"
    ? (recallState ? Math.round(recallState.recall) : completeness)
    : complMode === "all"
    ? (overallPct != null ? Math.round(overallPct) : completeness)
    : completeness;

  const EF = ({ id, l, v, c, n, s, path }) => {
    const confState = confirmed[id]; // "auto" | "manual" | undefined
    // Show the edited value if the user changed this field (tracked by path).
    const edited = path && (path in edits) ? edits[path] : undefined;
    const shownV = edited !== undefined ? edited : v;
    const isDirty = edited !== undefined && edited !== (v || "");
    const realC = isDirty ? "high" : (confState || (c === "medium" ? "medium" : c));
    const bc = (realC==="high"||realC==="auto"||realC==="manual")?T.accent:realC==="medium"?T.amber:T.red;
    const isEd = editingField===id;
    return (
      <div style={{ marginBottom: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 3 }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: T.textSec, textTransform: "uppercase", letterSpacing: "0.05em" }}>{l}</span>
          <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
            {realC==="medium"&&<button onClick={() => doConfirm(id)} style={{ fontSize: 10, fontWeight: 600, color: T.accentDark, background: T.accentSoft, border: "none", borderRadius: 3, padding: "1px 6px", cursor: "pointer", display: "flex", alignItems: "center", gap: 2 }}><I d={ic.check} size={9} color={T.accentDark} /> {_("confirm")}</button>}
            <Conf c={confState === "manual" ? "manual" : confState === "auto" ? "high" : (c === "high" ? "high" : realC)} onClick={realC==="medium" ? () => doConfirm(id) : undefined} />
          </div>
        </div>
        <div onClick={() => setEditingField(isEd?null:id)} onBlur={() => { if (isEd && c === "medium") setConfirmed(p => ({...p, [id]: "manual"})); }} style={{ padding: "9px 12px", borderRadius: 6, border: isEd?`2px solid ${T.accent}`:`1px solid ${bc}30`, borderLeft: `3px solid ${bc}`, background: isEd?T.accentSoft+"30":T.bg, fontSize: 13, color: shownV?T.textDark:T.textSec, fontStyle: shownV?"normal":"italic", cursor: "text", lineHeight: 1.5 }}>
          {isEd?<input autoFocus defaultValue={shownV ?? ""} onChange={e => path && setEdits(p => ({ ...p, [path]: e.target.value }))} style={{ width: "100%", border: "none", outline: "none", fontSize: 13, fontWeight: 600, color: T.textDark, background: "transparent", fontFamily: font }} />:(shownV||"Missing data — click to enter")}
        </div>
        {s&&!n&&<div style={{ fontSize: 10, color: T.textSec, marginTop: 2, paddingLeft: 14, display: "flex", alignItems: "center", gap: 3, cursor: "pointer" }} title="Click to view source document"><I d={ic.file} size={10} color={T.textSec} /> {_("source")}: <span style={{ textDecoration: "underline", color: T.accentDark }}>{s}</span></div>}
        {n&&!confState&&<div style={{ marginTop: 4, padding: "6px 10px", borderRadius: 5, background: c==="low"?T.redSoft:T.amberSoft, fontSize: 11, color: c==="low"?T.red:"#92400E", lineHeight: 1.5, display: "flex", gap: 6 }}><I d={c==="low"?ic.alert:ic.bolt} size={12} color={c==="low"?T.red:T.amber} /><span>{n}{s?` (${_("source")}: ${s})`:""}</span></div>}
      </div>);};

  const Sec = ({ title, iconD, children }) => (
    <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden", marginBottom: 16 }}>
      <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.borderLight}`, display: "flex", alignItems: "center", gap: 7 }}><I d={iconD} size={16} color={T.accentDark} /><span style={{ fontSize: 14, fontWeight: 700, color: T.textDark }}>{title}</span></div>
      <div style={{ padding: "14px 16px" }}>{children}</div>
    </div>);

  const it = L?.lang === "it";
  // AppEditView shows only the core editing tabs.
  // Batch/Item creation moved to AppView (multi-level nav).
  const tabs = [
    { key:"panoramica", label:_("overview"), iconD:ic.chart, w:2, e:0 },
    { key:"composizione", label:_("composition"), iconD:ic.layers, w:0, e:0 },
    { key:"prestazioni", label:_("performance"), iconD:ic.bolt, w:2, e:0 },
    { key:"conformita", label:_("compliance"), iconD:ic.shield, w:0, e:1 },
    { key:"lifecycle", label:_("lifecycle"), iconD:ic.clock, w:0, e:0 },
    { key:"documenti", label:_("documents"), iconD:ic.file, w:0, e:0 },
  ];

  const [confirmed, setConfirmed] = useState({});
  const confFor = (id, orig) => confirmed[id] ? "high" : orig;
  const doConfirm = (id) => setConfirmed(p => ({ ...p, [id]: p[id] || "auto" }));

  const renderTab = () => {
    switch(tab){
    case "panoramica": return (<>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <ColSec title={_("productInfo")} iconD={ic.box} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("required")}</Badge>}>
          <EF id="nome" l={_("fProductName")} {...(hasAI ? d("overview.product_info.product_name") : {v:"XPS Insulation Panel 100mm",c:"high",s:"Technical Sheet, p. 1"})} />
          <EF id="uid" l="UID" {...(hasAI ? d("overview.product_info.uid") : {v:"DPP-20260115-a3f8c2d1",c:"high",s:"Generated"})} />
          <EF id="tipo" l={_("fItemType")} {...(hasAI ? d("overview.product_info.item_type") : {v:"Product",c:"high",s:"Automatic"})} />
          <EF id="cat" l={_("fCprCategory")} {...(hasAI ? d("overview.product_info.product_family") : {v:"Thermal insulation products",c:confFor("cat","medium"),s:"DoP",n:"Classified as CPR Annex VII — Thermal insulation. Please confirm."})} />
          <EF id="uf" l={_("fFuncUnit")} {...(hasAI ? d("overview.product_info.functional_unit") : {v:"1 m² thickness 100mm",c:confFor("uf","medium"),s:"EPD, pag. 2",n:"EPD declares 1m² thickness 100mm. Please verify with DoP."})} />
          <EF id="desc" l={_("fDescription")} {...(hasAI ? d("overview.product_info.product_description") : {v:"High-density extruded polystyrene insulation panel for thermal insulation.",c:"high",s:"Technical Data Sheet"})} />
          <EF id="dim" l={_("fDimensions")} {...(hasAI ? d("overview.product_info.standard_dimension") : {v:"1250 × 600 × 100 mm",c:"high",s:"Technical Data Sheet"})} />
          <EF id="peso" l={_("fWeight")} {...(hasAI ? d("overview.product_info.weight") : {v:"3.5 kg/m²",c:"high",s:"Technical Data Sheet"})} />
        </ColSec>
        <ColSec title={_("manufacturer")} iconD={ic.factory} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("required")}</Badge>}>
          <EF id="prod" l={_("fCompany")} {...(hasAI ? d("overview.manufacturer.company_name") : {v:"Deeppy Construction Materials srl",c:"high",s:"DoP"})} />
          <EF id="sede" l={_("fLegalHQ")} {...(hasAI ? d("overview.manufacturer.address") : {v:"Via Emilia 42, 47921 Rimini (RN), Italia",c:"high",s:"Profile"})} />
          <EF id="stab" l={_("fProdSite")} {...(hasAI ? d("overview.manufacturer.manufacturing_site") : {v:"Stabilimento Novara, Via Industria 8, 28100 Novara",c:confFor("stab","medium"),s:"DoP, pag. 1",n:"DoP reports Novara plant. Please confirm."})} />
          <EF id="web" l={_("fWebsite")} {...(hasAI ? d("overview.manufacturer.website") : {v:"www.deeppy-materials.it",c:"high",s:"Profile"})} />
          <EF id="contact" l={_("fDataContact")} {...(hasAI ? d("overview.manufacturer.email") : {v:"a.pracucci@levery.it",c:"high",s:"Profile"})} />
          <EF id="phone" l={L?.lang==="it"?"Telefono":"Phone"} {...(hasAI ? d("overview.manufacturer.phone") : {v:"+39 0541 123456",c:"high",s:"Profile"})} />
          <EF id="certaz" l={_("fCompCerts")} v="ISO 9001:2015, ISO 14001:2015" c="high" s="Profile" />
        </ColSec>
      </div>
      <ColSec title={_("optionalInfo")} iconD={ic.file} defaultOpen={false} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("optional")}</Badge>}>
        <EF id="gtin" l="GTIN" {...(hasAI ? d("overview.product_info.gtin") : {v:"",c:"low",n:"Not found in documents. Optional."})} />
        <EF id="bn" l={_("fBatchSerial")} {...(hasAI ? d("overview.product_info.batch_number") : {v:"",c:"low",n:"Optional. Enter if applicable."})} />
        <EF id="img" l={_("fProdImage")} {...(hasAI ? d("overview.product_info.product_image") : {v:L?.lang==="it"?"📷 Caricata (XPS-100mm.jpg)":"📷 Uploaded (XPS-100mm.jpg)",c:"high",s:"Upload"})} />
        <EF id="vendita" l={_("fSaleType")} {...(hasAI ? d("overview.manufacturer.sale_type") : {v:"Direct sales, Retailers",c:"high",s:"Profile"})} />
        <EF id="dataprod" l={_("fMfgDate")} {...(hasAI ? d("overview.product_info.production_period") : {v:"",c:"low",n:"Optional. Applicable to specific batch."})} />
      </ColSec>
      <ColSec title={_("versionHistory")} iconD={ic.clock} defaultOpen={false}>
        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
          {[
            { ver: "v1.2", date: "Feb 18, 2026", label: "Current", docs: "+FPC Certificate", fields: "+3 fields" },
            { ver: "v1.1", date: "Jan 28, 2026", docs: "+Safety Data Sheet", fields: "+7 fields" },
            { ver: "v1.0", date: "Jan 15, 2026", label: "First release", docs: "DoP, Technical Sheet, EPD" },
          ].map((v, i) => (
            <div key={i} style={{ display: "flex", gap: 12, paddingBottom: 12, marginBottom: i < 2 ? 12 : 0, borderBottom: i < 2 ? `1px solid ${T.borderLight}` : "none" }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flexShrink: 0 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: i === 0 ? T.accent : T.border }} />
                {i < 2 && <div style={{ width: 1, flex: 1, background: T.border, marginTop: 4 }} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                  <span style={{ fontSize: 13, fontWeight: 700, color: T.textDark }}>{v.ver}</span>
                  <span style={{ fontSize: 11, color: T.textSec }}>{v.date}</span>
                  {v.label && <Badge color={i === 0 ? T.accentDark : T.textSec} bg={i === 0 ? T.accentSoft : T.bgSoft}>{v.label}</Badge>}
                </div>
                <div style={{ fontSize: 12, color: T.textSec }}>{v.docs}{v.fields ? ` — ${v.fields}` : ""}</div>
              </div>
            </div>
          ))}
        </div>
      </ColSec>
      <div style={{ marginTop: 4 }}><SupplyMap dppData={dppData} /></div>
    </>);
    case "composizione": return (<ComponentiTab editMode={true} onNavigate={onNavigate} L={L} dppData={dppData} />);
    case "prestazioni": {
      const perfValues = hasAI ? (pp?.performance?.values || []) : null;
      const byCategory = perfValues ? perfValues.reduce((acc, pv) => {
        const cat = pv.category || "Other";
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(pv);
        return acc;
      }, {}) : null;
      const catIcons = { Mechanical: ic.shield, Thermal: ic.thermo, Fire: ic.alert, Acoustic: ic.bolt, Durability: ic.leaf, Environmental: ic.leaf, Other: ic.chart };
      const catLabels = { Mechanical: _("mechPerf"), Thermal: _("thermPerf"), Fire: L?.lang==="it"?"Reazione al fuoco":"Fire reaction", Acoustic: _("acoustics"), Durability: _("durability"), Environmental: L?.lang==="it"?"Ambientale":"Environmental", Other: L?.lang==="it"?"Altro":"Other" };

      if (hasAI && byCategory) {
        return (<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {Object.entries(byCategory).map(([cat, props]) => (
            <ColSec key={cat} title={catLabels[cat] || cat} iconD={catIcons[cat] || ic.bolt} badge={<Badge color={T.textSec} bg={T.bgSoft}>{props.length}</Badge>}>
              {props.map((pv, i) => {
                const fld = pv.value || {};
                const src = fld.source;
                const srcStr = src ? (typeof src === "string" ? src : `${src.document_name||""}${src.page?`, p. ${src.page}`:""}`) : null;
                const unitStr = pv.unit ? ` ${pv.unit}` : "";
                const stdStr = pv.test_standard ? ` — ${pv.test_standard}` : "";
                return <EF key={i} id={`perf-${cat}-${i}`} l={pv.property_name} v={fld.value != null ? `${fld.value}${unitStr}` : null} c={fld.confidence||"low"} s={srcStr ? `${srcStr}${stdStr}` : null} n={fld.note} />;
              })}
            </ColSec>
          ))}
        </div>);
      }

      return (<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <ColSec title={_("mechPerf")} iconD={ic.shield} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("required")}</Badge>}>
          <EF id="comp" l={_("fCompStrength")} v="300 kPa" c="high" s="DoP — EN 826" />
          <EF id="flex" l={_("fFlexStrength")} v="≥ 500 kPa" c={confFor("flex","medium")} s="Technical Data Sheet" n="Value ≥ 500 kPa. DoP: CS(10\\Y)300. Please verify." />
          <EF id="traz" l={_("fTensStrength")} v="≥ 200 kPa" c="high" s="DoP — EN 1607" />
          <EF id="elast" l={_("fElastMod")} v="25 MPa" c="high" s="Technical Data Sheet" />
          <EF id="urto" l={_("fImpactRes")} v="Classe 2" c={confFor("urto","medium")} s="Calculated" n="Derived from technical data sheet. Please confirm." />
        </ColSec>
        <ColSec title={_("thermPerf")} iconD={ic.thermo} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("required")}</Badge>}>
          <EF id="lambda" l={_("fThermCond")} v="0.034 W/(m·K)" c="high" s="DoP — EN 12667" />
          <EF id="r" l={_("fThermRes")} v="2.94 m²·K/W" c="high" s="DoP" />
          <EF id="fuoco" l={_("fFireClass")} v="E" c="high" s="DoP — EN 13501-1" />
          <EF id="espans" l={_("fExpCoeff")} v="0.07 mm/(m·K)" c="high" s="Technical Data Sheet" />
        </ColSec>
        <ColSec title={_("acoustics")} iconD={ic.bolt} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("optional")}</Badge>} defaultOpen={false}>
          <EF id="fonoass" l={_("fSoundAbs")} v="" c="low" n="Not found in uploaded documents." />
          <EF id="fonoisol" l={_("fSoundIns")} v="" c="low" n="Not found in uploaded documents." />
        </ColSec>
        <ColSec title={_("moisture")} iconD={ic.droplet} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("required")}</Badge>}>
          <EF id="assorb" l={_("fWaterAbs")} v="≤ 0.7% vol" c="high" s="DoP — EN 12087" />
          <EF id="vapore" l={_("fVaporPerm")} v="80-250" c="high" s="Technical Data Sheet" />
          <EF id="gelo" l={_("fFreezeThaw")} v="Compliant" c="high" s="DoP" />
        </ColSec>
        <ColSec title={_("durability")} iconD={ic.leaf} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("optional")}</Badge>} defaultOpen={false}>
          <EF id="uv" l={_("fUvRes")} v="Protection required" c={confFor("uv","medium")} s="Technical Data Sheet" n="XPS requires UV protection. Details in technical data sheet." />
          <EF id="corr" l={_("fCorrRes")} v="N/A (non-metallic)" c="high" s="Automatic" />
          <EF id="chim" l={_("fChemRes")} v="Resistant to saline solutions, weak alkalis" c="high" s="Technical Data Sheet" />
        </ColSec>
      </div>);
    }
    case "conformita": return (<>
      <ColSec title={_("declarations")} iconD={ic.clip} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("required")}</Badge>}>
        <EF id="dop" l={_("fDoP")} {...(hasAI ? d("compliance.dop_reference") : {v:"DoP N. XPS-100-2026-001",c:"high",s:"DoP-XPS100-2026-001.pdf"})} />
        <EF id="dopstd1" l={_("fRefStandard")} {...(hasAI ? d("compliance.dop_standard") : {v:"EN 13164:2012+A1:2015",c:"high",s:"DoP"})} />
        <EF id="doc2" l={_("fDoC")} {...(hasAI ? d("compliance.doc_reference") : {v:"",c:"low",n:"Not uploaded. Optional."})} />
        <EF id="ce" l={_("fCeMark")} {...(hasAI ? d("compliance.ce_marking") : {v:L?.lang==="it"?"Conforme — Certificato CE n. 0123-CPR-2024":"Compliant — CE Certificate n. 0123-CPR-2024",c:"high",s:"CE Certificate"})} />
        <EF id="qc" l={_("fQC")} {...(hasAI ? d("compliance.quality_control") : {v:"FPC Certificate n. 0123-CPR-FPC",c:"high",s:"FPC Certificate"})} />
      </ColSec>
      <ColSec title={_("prodSafety")} iconD={ic.alert} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("required")}</Badge>}>
        <EF id="cmr" l={_("fCmr")} {...(hasAI ? d("compliance.safety.contains_cmrs") : {v:"No",c:"high",s:"Safety Data Sheet"})} />
        <EF id="svhc" l={_("fSvhc")} {...(hasAI ? d("compliance.safety.contains_svhcs") : {v:"No",c:"high",s:"Safety Data Sheet"})} />
        <EF id="pentano" l={_("fPentane")} {...(hasAI ? d("compliance.safety.contains_pentane") : {v:"Yes (blowing agent, < 2%)",c:confFor("pent","medium"),s:"EPD, Tabella 2",n:"Pentane used as blowing agent. Residual amount < 2%. Please confirm."})} />
        <EF id="pfas" l={_("fPfas")} {...(hasAI ? d("compliance.safety.contains_pfas") : {v:"No",c:"high",s:"Declaration"})} />
        <EF id="ritardanti" l={_("fFlameRet")} {...(hasAI ? d("compliance.safety.has_flame_retardancy") : {v:"Yes (HBCD-free, polymeric)",c:"high",s:"Safety Data Sheet"})} />
        <EF id="rohs" l={_("fRohs")} {...(hasAI ? d("compliance.safety.complies_rohs") : {v:"Yes",c:"high",s:"Certificate"})} />
        <EF id="voc" l={L?.lang==="it"?"Emissioni VOC?":"VOC emissions?"} {...(hasAI ? d("compliance.safety.produces_voc") : {v:"No",c:"high",s:"Safety Data Sheet"})} />
        <EF id="heavymetals" l={L?.lang==="it"?"Metalli pesanti o alogenati?":"Heavy metals or halogenated?"} {...(hasAI ? d("compliance.safety.contains_heavy_metals") : {v:"No",c:"high",s:"Safety Data Sheet"})} />
        <EF id="asbestos" l={L?.lang==="it"?"Contiene amianto?":"Contains asbestos?"} {...(hasAI ? d("compliance.safety.contains_asbestos") : {v:"No",c:"high",s:"Declaration"})} />
        <EF id="child" l={_("fChildLabor")} {...(hasAI ? d("compliance.safety.complies_child_labor") : {v:"Yes",c:"high",s:"Declaration"})} />
      </ColSec>
      <ColSec title={_("prodCerts")} iconD={ic.check} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("optional")}</Badge>} defaultOpen={false}>
        {hasAI && pp?.compliance?.product_certifications?.length > 0 ? pp.compliance.product_certifications.map((cert, i) => (
          <EF key={i} id={`cert-${i}`} l={cert.name?.value || `Certificate ${i+1}`} {..._ef(cert, "reference_number")} />
        )) : (<>
          <EF id="epd" l="EPD" v="EPD-XPS100-2025 — EPD Hub" c="high" s="EPD-XPS100-2025.pdf" />
          <EF id="cam" l="CAM (DM 23/06/2022)" v="" c="low" n="CAM data not found. Required: recycled content, VOC report, REACH." />
          <EF id="c2c" l="Cradle to Cradle" v="" c="low" n="Not available." />
        </>)}
      </ColSec>
      <ColSec title={_("compCerts")} iconD={ic.factory} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("optional")}</Badge>} defaultOpen={false}>
        {hasAI && pp?.compliance?.company_certifications?.length > 0 ? pp.compliance.company_certifications.map((cert, i) => (
          <EF key={i} id={`ccert-${i}`} l={cert.name?.value || `Certification ${i+1}`} {..._ef(cert, "reference_number")} />
        )) : (<>
          <EF id="iso9001" l="ISO 9001:2015" v="Certificato n. QMS-2024-0456" c="high" s="Company profile" />
          <EF id="iso14001" l="ISO 14001:2015" v="Certificato n. EMS-2024-0789" c="high" s="Company profile" />
          <EF id="iso45001" l="ISO 45001" v="" c="low" n="Not available." />
        </>)}
      </ColSec>
    </>);
    case "lifecycle": return (<LifecycleTab L={L} dppData={dppData} />);
    case "documenti": {
      const sourceDocs = hasAI ? (pp?.metadata?.source_documents || []) : ["DoP-XPS100-2026-001.pdf","Scheda-Tecnica-XPS100.pdf","EPD-XPS100-2025.pdf"];
      return (<>
      <ColSec title={_("analyzedDocs")} iconD={ic.file} badge={<Badge color={T.accentDark} bg={T.accentSoft}>{sourceDocs.length} file</Badge>}>
        {sourceDocs.map((name,i)=>(
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: i<sourceDocs.length-1?`1px solid ${T.borderLight}`:"none" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}><div style={{ width: 34, height: 34, borderRadius: 7, background: T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.file} size={16} color={T.accentDark} /></div><div><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{typeof name === "string" ? name : name.name}</div></div></div>
            <Badge color={T.accentDark} bg={T.accentSoft}><I d={ic.check} size={9} color={T.accentDark} /> {L?.lang==="it"?"Analizzato":"Analyzed"}</Badge>
          </div>))}
      </ColSec>
      <ColSec title={_("techDocs")} iconD={ic.tool} badge={<Badge color={T.textSec} bg={T.bgSoft}>{_("optional")}</Badge>} defaultOpen={false}>
        <EF id="inst" l={_("fInstMethod")} v="" c="low" n="Not uploaded. Optional." />
        <EF id="maint" l={_("fMaintMethod")} v="" c="low" n="Not uploaded. Optional." />
        <EF id="replace" l={L?.lang==="it"?"Istruzioni sostituzione/ripristino":"Method Statement for Replacement"} v="" c="low" n="Not uploaded. Optional." />
        <EF id="dismantling" l={L?.lang==="it"?"Istruzioni smontaggio e fine vita":"Method Statement for Dismantling & EoL"} v="" c="low" n="Not uploaded. Optional." />
        <EF id="draw2d" l={_("fDraw2d")} v="" c="low" n="Not uploaded. Formats: DWG, PDF." />
        <EF id="draw3d" l={_("fDraw3d")} v="" c="low" n="Not uploaded. Formats: IFC, RVT." />
      </ColSec>
      <ColSec title={_("otherDecl")} iconD={ic.clip} defaultOpen={false}>
        <EF id="climate" l={_("fClimateDecl")} v="" c="low" n="Not uploaded. Optional." />
        <EF id="otherdoc" l={_("fOtherDoc")} v="" c="low" n="Upload additional documents if needed." />
      </ColSec>
      <div onClick={()=>setShowUpload(!showUpload)} style={{ marginTop: 10, padding: "14px 0", border: `1px dashed ${T.border}`, borderRadius: 10, textAlign: "center", cursor: "pointer", background: T.bg }}><span style={{ fontSize: 13, fontWeight: 600, color: T.accentDark, display: "inline-flex", alignItems: "center", gap: 4 }}><I d={ic.plus} size={14} color={T.accentDark} /> Carica documenti aggiuntivi</span></div>
      {showUpload&&<div style={{ marginTop: 10, padding: 24, borderRadius: 8, border: `2px dashed ${T.accent}`, textAlign: "center", background: T.accentSoft+"30" }}><I d={ic.upload} size={28} color={T.accent} /><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark, marginTop: 6 }}>Trascina qui i nuovi documenti</div></div>}
    </>);
    }
    case "batch": return (<div>
      {!projCreated ? (<div style={{ textAlign: "center", padding: "40px 20px" }}>
        <div style={{ width: 64, height: 64, borderRadius: 16, background: T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}><I d={ic.clip} size={28} color={T.accentDark||T.accent} /></div>
        <h3 style={{ fontSize: 18, fontWeight: 700, color: T.navy, margin: "0 0 6px" }}>{it?"Crea DPP Batch":"Create Batch DPP"}</h3>
        <p style={{ fontSize: 13, color: T.textSec, maxWidth: 440, margin: "0 auto 24px", lineHeight: 1.5 }}>{it?"Carica un documento di progetto (ordine di produzione, distinta materiali) per estrarre automaticamente le informazioni, oppure compila manualmente i campi sotto.":"Upload a project document (production order, bill of materials) to auto-extract information, or fill in the fields below manually."}</p>
        <div style={{ maxWidth: 420, margin: "0 auto 20px", padding: "16px 18px", borderRadius: 10, border: `2px dashed ${T.accent}`, background: T.accentSoft+"20", cursor: "pointer" }}>
          <I d={ic.upload} size={24} color={T.accent} />
          <div style={{ fontSize: 13, fontWeight: 600, color: T.accentDark||T.accent, marginTop: 6 }}>{it?"Carica documento di progetto":"Upload project document"}</div>
          <div style={{ fontSize: 11, color: T.textSec, marginTop: 2 }}>{it?"Ordine di produzione, distinta materiali, specifica tecnica...":"Production order, bill of materials, technical specification..."}</div>
        </div>
        <div style={{ maxWidth: 420, margin: "0 auto", display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}><div style={{ flex: 1, height: 1, background: T.border }} /><span style={{ fontSize: 11, color: T.textSec, fontWeight: 600 }}>{it?"oppure compila manualmente":"or fill manually"}</span><div style={{ flex: 1, height: 1, background: T.border }} /></div>
        <div style={{ maxWidth: 420, margin: "0 auto", textAlign: "left" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
            <div><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Lotto di produzione *":"Production batch *"}</div><input value={projBatch} onChange={e=>setProjBatch(e.target.value)} placeholder={it?"Es. PR-2026-047":"E.g. PR-2026-047"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} /></div>
            <div><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Stabilimento *":"Production site *"}</div><input value={projSite} onChange={e=>setProjSite(e.target.value)} placeholder={it?"Es. Stabilimento Treviso":"E.g. Treviso plant"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} /></div>
          </div>
          <div style={{ marginBottom: 10 }}><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Riferimento commessa / cliente":"Order / client reference"}</div><input value={projRef} onChange={e=>setProjRef(e.target.value)} placeholder={it?"Es. Commessa Villa Marchetti":"E.g. Order Villa Marchetti"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} /></div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
            <div><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Dimensioni reali":"Actual dimensions"}</div><input value={projDims} onChange={e=>setProjDims(e.target.value)} placeholder={it?"Es. 1200\u00d71500mm":"E.g. 1200\u00d71500mm"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} /></div>
            <div><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Peso reale":"Actual weight"}</div><input value={projWeight} onChange={e=>setProjWeight(e.target.value)} placeholder={it?"Es. 38 kg":"E.g. 38 kg"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} /></div>
          </div>
          <div style={{ marginBottom: 14 }}><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Note progetto":"Project notes"}</div><textarea value={projNotes} onChange={e=>setProjNotes(e.target.value)} rows={2} placeholder={it?"Informazioni aggiuntive...":"Additional information..."} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none", resize: "vertical" }} /></div>
          <div style={{ padding: "12px 14px", borderRadius: 8, border: `1px dashed ${T.border}`, textAlign: "center", marginBottom: 14, cursor: "pointer", background: T.bgSoft }}><I d={ic.upload} size={16} color={T.textSec} /><div style={{ fontSize: 11, color: T.textSec, marginTop: 4 }}>{it?"Carica documenti di progetto (ordine, distinta materiali...)":"Upload project documents (order, bill of materials...)"}</div></div>
          <Btn primary onClick={() => {
            onAddProjectDPP && onAddProjectDPP({ batch: projBatch, site: projSite, ref: projRef, dims: projDims, weight: projWeight, notes: projNotes });
            setProjCreated(true); setProjBatch(""); setProjSite(""); setProjRef(""); setProjDims(""); setProjWeight(""); setProjNotes("");
          }} style={{ width: "100%", justifyContent: "center" }} disabled={!projBatch || !projSite}><I d={ic.plus} size={14} color={T.navy} /> {it?"Crea DPP Progetto":"Create Project DPP"}</Btn>
        </div>
      </div>) : (<div>
        <div style={{ padding: "14px 16px", borderRadius: 10, background: T.accentSoft+"40", border: `1px solid ${T.accent}30`, marginBottom: 16, display: "flex", alignItems: "center", gap: 10 }}>
          <I d={ic.check} size={16} color={T.accentDark||T.accent} />
          <div><div style={{ fontSize: 13, fontWeight: 700, color: T.accentDark||T.accent }}>{it?"DPP Progetto creato":"Project DPP created"}</div><div style={{ fontSize: 11, color: T.textSec }}>{it?"QR code dedicato disponibile nella sezione export":"Dedicated QR code available in export section"}</div></div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <Card title={it?"Informazioni Progetto":"Project Information"} iconD={ic.clip}>
            <Row l={it?"Lotto di produzione":"Production batch"} v={projBatch} />
            <Row l={it?"Stabilimento":"Production site"} v={projSite} />
            {projRef && <Row l={it?"Commessa / Cliente":"Order / Client"} v={projRef} />}
            {projDims && <Row l={it?"Dimensioni reali":"Actual dimensions"} v={projDims} />}
            {projWeight && <Row l={it?"Peso reale":"Actual weight"} v={projWeight} />}
            {projNotes && <Row l={it?"Note":"Notes"} v={projNotes} />}
          </Card>
          <Card title={it?"Documenti Progetto":"Project Documents"} iconD={ic.file}>
            <div style={{ padding: "20px 18px", textAlign: "center" }}>
              <div style={{ padding: "12px 14px", borderRadius: 8, border: `1px dashed ${T.border}`, cursor: "pointer", background: T.bgSoft }}><I d={ic.upload} size={16} color={T.textSec} /><div style={{ fontSize: 11, color: T.textSec, marginTop: 4 }}>{it?"Carica documenti di progetto":"Upload project documents"}</div></div>
            </div>
          </Card>
        </div>
      </div>)}
    </div>);
    case "item": return (<div style={{ textAlign: "center", padding: "32px 20px" }}>
      <div style={{ width: 48, height: 48, borderRadius: 12, background: T.blueSoft||"#EFF6FF", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 12px" }}><I d={ic.box} size={22} color="#3B82F6" /></div>
      <h3 style={{ fontSize: 16, fontWeight: 700, color: T.navy, margin: "0 0 4px" }}>{it?"DPP Item":"Item DPP"}</h3>
      <p style={{ fontSize: 12, color: T.textSec, maxWidth: 380, margin: "0 auto 16px" }}>{it?"Crea un DPP per singolo prodotto. Eredita dal Batch o dal Model.":"Create a DPP for individual product. Inherits from Batch or Model."}</p>
      <Btn primary onClick={()=>onNavigate("onboard-item")} style={{ margin: "0 auto" }}><I d={ic.upload} size={14} color={T.navy} /> {it?"Carica documenti":"Upload documents"}</Btn>
    </div>);
    case "versioni": {
      const versions = [
        { ver: "v2.3", date: "2 Mar 2026", author: "Sistema", changes: [
          { type: "updated", field: it?"Resistenza termica R":"Thermal resistance R", from: "2.85", to: "2.94 m²·K/W", section: it?"Dati Tecnici":"Technical" },
          { type: "added", field: "EPD", detail: "EPD-EDT-2024-0847", section: it?"Documenti":"Documents" },
        ]},
        { ver: "v2.2", date: "18 Feb 2026", author: "M. Rossi", changes: [
          { type: "updated", field: it?"Contenuto riciclato":"Recycled content", from: "8%", to: "12%", section: it?"Ambiente":"Environment" },
          { type: "updated", field: "GWP", from: "3.8", to: "3.4 kg CO₂ eq/m²", section: it?"Ambiente":"Environment" },
          { type: "added", field: "CAM", detail: it?"Certificazione":"Certification", section: it?"Certificazioni":"Certifications" },
        ]},
        { ver: "v2.0", date: "20 Gen 2026", author: "Sistema", changes: [
          { type: "added", field: "CE", detail: "CE-0432-CPR-2024", section: it?"Certificazioni":"Certifications" },
          { type: "updated", field: it?"Completezza":"Completeness", from: "67%", to: "87%", section: it?"Generale":"General" },
        ]},
        { ver: "v1.0", date: "15 Gen 2026", author: "Sistema", changes: [
          { type: "created", field: "DPP", detail: it?"Estrazione automatica":"Auto-extraction", section: it?"Generale":"General" },
        ]},
      ];
      const chSt2 = { created: { color: T.accent, bg: T.accentSoft, d: ic.plus }, added: { color: T.accentDark||T.accent, bg: T.accentSoft, d: ic.plus }, updated: { color: "#3B82F6", bg: "#EFF6FF", d: ic.edit }, removed: { color: T.red, bg: T.redSoft||"#FEE2E2", d: ic.close } };
      return (<Card title={it?"Cronologia Versioni":"Version History"} iconD={ic.clock}><div style={{ padding: "16px 18px" }}>{versions.map((v,vi)=>{const isFirst=vi===versions.length-1;const isLast=vi===0;return(<div key={vi} style={{ position: "relative", paddingLeft: 28, marginBottom: 6 }}>{vi<versions.length-1&&<div style={{ position: "absolute", left: 9, top: 22, bottom: -2, width: 2, background: T.border }} />}<div style={{ position: "absolute", left: 3, top: 6, width: 14, height: 14, borderRadius: "50%", background: isLast ? T.accent : isFirst ? T.navy : T.bg, border: `2.5px solid ${isLast ? T.accent : isFirst ? T.navy : T.border}`, zIndex: 2 }} /><div style={{ padding: "10px 14px", borderRadius: 8, border: `1px solid ${T.borderLight}`, background: T.bg }}><div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}><div style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ fontSize: 13, fontWeight: 700, color: T.navy, fontFamily: "'JetBrains Mono',monospace" }}>{v.ver}</span>{isLast&&<Badge color={T.accentDark||T.accent} bg={T.accentSoft}>{it?"ATTUALE":"CURRENT"}</Badge>}</div><span style={{ fontSize: 11, color: T.textSec }}>{v.date} · {v.author}</span></div><div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>{v.changes.map((ch,ci)=>{const st=chSt2[ch.type]||chSt2.added;return(<span key={ci} style={{ display: "inline-flex", alignItems: "center", gap: 3, padding: "2px 7px", borderRadius: 4, fontSize: 10, fontWeight: 600, color: st.color, background: st.bg }}><I d={st.d} size={9} color={st.color} />{ch.field}{ch.from?" → "+ch.to:""}</span>);})}</div></div></div>);})}</div></Card>);
    }
    default: return null;}};

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: font, background: T.bgSoft, overflow: "hidden" }}>
      <Sidebar activePage="passaporti" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 28px 40px" }}>
          <button onClick={()=>onNavigate("catalog")} style={{ background: "none", border: "none", color: T.textSec, fontSize: 12, cursor: "pointer", padding: 0, marginBottom: 12, fontFamily: font, display: "flex", alignItems: "center", gap: 4 }}><I d={ic.arrow} size={12} color={T.textSec} style={{ transform: "rotate(180deg)" }} /> {_("backTo")}</button>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div style={{ display: "flex", gap: 6, marginBottom: 6 }}>
                {product?.status === "published"
                  ? <Badge color={T.accentDark} bg={T.accentSoft}><I d={ic.check} size={9} color={T.accentDark} /> {_("published")}</Badge>
                  : <Badge color={T.amber} bg={T.amberSoft}><I d={ic.edit} size={9} color={T.amber} /> {_("draft")}</Badge>}
                <Badge color={T.textSec} bg={T.bgSoft}>{hasAI ? ((pp?.overview?.product_info?.product_family?.value || "").split(" - ")[0] || pp?.overview?.product_info?.product_family_code?.value || _("insulation")) : _("insulation")}</Badge>
                <Badge color={T.textSec} bg={T.bgSoft}><I d={ic.globe} size={9} color={T.textSec} /> EU 2024/1781</Badge>
              </div>
              <h1 style={{ fontSize: 24, fontWeight: 800, color: T.navy, margin: "0 0 3px" }}>{hasAI ? (pp?.overview?.product_info?.product_name?.value || "Product") : "XPS Insulation Panel 100mm"}</h1>
              <div style={{ fontSize: 12, color: T.textSec }}>{`${hasAI ? (pp?.overview?.product_info?.uid?.value || "—") : "DPP-20260115-a3f8c2d1"}${(() => { const ts = product?.updatedAt || product?.createdAt; if (!ts) return ""; const d = new Date(ts); return isNaN(d) ? "" : ` — ${L?.lang==="it"?"Aggiornato":"Updated"}: ${d.toLocaleDateString(L?.lang==="it"?"it-IT":"en-US",{day:"numeric",month:"short",year:"numeric"})}`; })()}`}</div>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <Btn small onClick={()=>setChatOpen(!chatOpen)} style={{ border: `1px solid ${chatOpen?T.accent:T.border}`, background: chatOpen?T.accentSoft:T.bg, color: chatOpen?T.accentDark:T.textSec }}><I d={ic.msg} size={13} color={chatOpen?T.accentDark:T.textSec} /> {_("assistant")}</Btn>
              <Btn small onClick={handleSave}>{saved?<><I d={ic.check} size={13} color={T.accentDark} /> {_("saved")}</>:_("saveDraft")}</Btn>
              <Btn small primary onClick={()=>onNavigate("app")}>{_("preview")} <I d={ic.arrow} size={13} color={T.navy} /></Btn>
            </div>
          </div>
          {/* Document update upload zone */}
          <div style={{ marginBottom: 16, padding: "14px 18px", background: T.bg, borderRadius: 10, border: `1px dashed ${updateFiles.length > 0 ? T.accent : T.border}`, transition: "border .2s" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: updateFiles.length > 0 ? 10 : 0 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <I d={ic.upload} size={16} color={updateFiles.length > 0 ? T.accentDark : T.textSec} />
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: T.textDark }}>{L?.lang==="it"?"Aggiorna documenti":"Update documents"}</div>
                  <div style={{ fontSize: 11, color: T.textSec }}>{L?.lang==="it"?"Carica nuovi documenti per aggiornare il DPP (EPD, DoP, certificati, schede tecniche)":"Upload new documents to update the DPP (EPD, DoP, certificates, technical sheets)"}</div>
                </div>
              </div>
              <label style={{ cursor: "pointer" }}>
                <input type="file" multiple style={{ display: "none" }} onChange={e => { if (e.target.files?.length) setUpdateFiles(prev => [...prev, ...Array.from(e.target.files).map(f => f.name)]); }} />
                <Btn small as="span" style={{ pointerEvents: "none" }}><I d={ic.upload} size={12} color={T.textDark} /> {L?.lang==="it"?"Sfoglia":"Browse"}</Btn>
              </label>
            </div>
            {updateFiles.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {updateFiles.map((f, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px", borderRadius: 6, background: T.accentSoft, fontSize: 11, fontWeight: 600, color: T.accentDark }}>
                    <I d={ic.file} size={10} color={T.accentDark} /> {f}
                    <button onClick={() => setUpdateFiles(prev => prev.filter((_, j) => j !== i))} style={{ background: "none", border: "none", cursor: "pointer", padding: 0, marginLeft: 2 }}><I d={ic.x} size={10} color={T.accentDark} /></button>
                  </div>
                ))}
                <Btn small primary onClick={() => { setUpdateProgress(true); setTimeout(() => { setUpdateProgress(false); setCompleteness(92); setUpdateFiles([]); }, 2000); }} style={{ marginLeft: "auto" }}>
                  <I d={ic.check} size={12} color={T.navy} /> {L?.lang==="it"?"Analizza e aggiorna":"Analyze & update"}
                </Btn>
              </div>
            )}
            {updateProgress && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: T.textSec, marginBottom: 4 }}>
                  <span>{L?.lang==="it"?"Analisi documenti in corso...":"Analyzing documents..."}</span>
                </div>
                <div style={{ width: "100%", height: 4, borderRadius: 2, background: T.border, overflow: "hidden" }}>
                  <div style={{ width: "60%", height: "100%", borderRadius: 2, background: `linear-gradient(90deg, ${T.accent}, ${T.accentDark})` }} />
                </div>
              </div>
            )}
          </div>
          <div style={{ marginBottom: 18, padding: "12px 16px", background: T.bg, borderRadius: 8, border: `1px solid ${T.border}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <div style={{ display: "flex", gap: 10, alignItems: "baseline" }}>
                <span style={{ fontSize: 22, fontWeight: 800, color: T.textDark }}>{displayedPct}%</span>
                <span style={{ fontSize: 13, color: T.textSec }}>{
                  complMode === "recall"
                    ? `${L?.lang==="it"?"vs atteso":"vs expected"}${recallState?` (${recallState.captured}/${recallState.total})`:""}`
                  : complMode === "all"
                    ? `${L?.lang==="it"?"tutti i campi":"all fields"}${allTotal!=null?` (${allFilled}/${allTotal})`:""}`
                    : `${L?.lang==="it"?"campi obbligatori":"required fields"}${reqTotal!=null?` (${reqFilled}/${reqTotal})`:""}`}</span>
                {/* Toggle: required / all / recall(vs expected) */}
                <div style={{ display: "inline-flex", border: `1px solid ${T.border}`, borderRadius: 6, overflow: "hidden", marginLeft: 4 }}>
                  {[["required", L?.lang==="it"?"Obbligatori":"Required"], ["all", L?.lang==="it"?"Tutti":"All"], ...(recallState ? [["recall", L?.lang==="it"?"vs Atteso":"vs Expected"]] : [])].map(([m, lbl]) => (
                    <button key={m} onClick={() => setComplMode(m)} style={{ padding: "3px 9px", border: "none", cursor: "pointer", fontFamily: font, fontSize: 10.5, fontWeight: 600, background: complMode===m?T.accentSoft:T.bg, color: complMode===m?T.accentDark:T.textSec }}>{lbl}</button>
                  ))}
                </div>
                {/* Attach expert expected-results file to enable recall */}
                <input ref={evalInputRef} type="file" accept=".xlsx,.xls" style={{ display: "none" }} onChange={e => { if (e.target.files?.[0]) uploadEval(e.target.files[0]); e.target.value=""; }} />
                <button onClick={() => evalInputRef.current?.click()} title={L?.lang==="it"?"Carica risultati attesi (XLSX) per calcolare il recall":"Upload expected results (XLSX) to compute recall"} style={{ marginLeft: 2, background: "none", border: "none", cursor: "pointer", fontFamily: font, fontSize: 10.5, fontWeight: 600, color: T.accentDark, display: "flex", alignItems: "center", gap: 3 }}><I d={ic.upload} size={11} color={T.accentDark} /> {recallState ? (L?.lang==="it"?"Aggiorna atteso":"Update expected") : (L?.lang==="it"?"Carica atteso":"Load expected")}</button>
              </div>
              <div style={{ display: "flex", gap: 12 }}>{[[T.accent,`${highCount} auto`],[T.amber,L?.lang==="it"?`${medCount} da confermare`:`${medCount} to review`],[T.red,L?.lang==="it"?`${lowCount} mancanti`:`${lowCount} missing`]].map(([c,l],i)=>(<span key={i} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12 }}><span style={{ width: 8, height: 8, borderRadius: "50%", background: c }} /><span style={{ color: T.textSec }}>{l}</span></span>))}</div>
            </div>
            <div style={{ width: "100%", height: 6, borderRadius: 3, background: T.border }}><div style={{ width: `${displayedPct}%`, height: "100%", borderRadius: 3, background: `linear-gradient(90deg, ${T.accent}, ${T.accentDark})`, transition: "width 0.5s ease" }} /></div>
          </div>
          <div style={{ display: "flex", gap: 2, marginBottom: 18, borderBottom: `1px solid ${T.border}` }}>
            {tabs.map(t=>(<button key={t.key} onClick={()=>setTab(t.key)} style={{ padding: "9px 16px", border: "none", borderBottom: `2px solid ${tab===t.key?T.accent:"transparent"}`, background: "transparent", fontSize: 13, fontWeight: tab===t.key?700:500, color: tab===t.key?T.textDark:T.textSec, cursor: "pointer", fontFamily: font, display: "flex", alignItems: "center", gap: 5, marginBottom: -1 }}>
              <I d={t.iconD} size={13} color={tab===t.key?T.accentDark:T.textSec} />{t.label}
              {t.w>0&&<span style={{ fontSize: 9, fontWeight: 700, color: T.amber, background: T.amberSoft, padding: "1px 5px", borderRadius: 3 }}>!{t.w}</span>}
              {t.e>0&&<span style={{ fontSize: 9, fontWeight: 700, color: T.red, background: T.redSoft, padding: "1px 5px", borderRadius: 3 }}>x{t.e}</span>}
            </button>))}
          </div>
          {renderTab()}
        </div>
        <ChatPanel open={chatOpen} onClose={()=>setChatOpen(false)} L={L} productId={product?.id} />
      </div>
    </div>);
}

// ─── CATALOG VIEW (post-login) ───────────────────────────
function CatalogView({ onNavigate, L }) {
  const _ = k => t(k, L?.lang);
  const it = L?.lang === "it";
  const [filter, setFilter] = useState(CATALOG_ALL_KEY);
  const [search, setSearch] = useState("");
  const [chatOpen, setChatOpen] = useState(false);
  const [selectedDPP, setSelectedDPP] = useState(null);
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [chatMsgs, setChatMsgs] = useState([{ from: "agent", text: it ? "Benvenuto nel catalogo DeePPy. Posso aiutarti a cercare prodotti per tipologia, prestazione o produttore." : "Welcome to the DeePPy catalog. I can help you search products by type, performance or manufacturer." }]);
  const [chatInput, setChatInput] = useState("");

  // Live catalog rows from /api/catalog — every published product across all
  // companies. Each row carries an is_own flag for the "yours" badge.
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch("/api/catalog", { credentials: "include" })
      .then(r => r.ok ? r.json() : [])
      .then(data => { if (!cancelled && Array.isArray(data)) setRows(data); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  // Category chips are derived from the data — show whatever family_codes the
  // published products actually have. "all" is always first.
  const families = Array.from(new Set(rows.map(r => r.family_code).filter(Boolean))).sort();

  const chatSend = () => {
    if (!chatInput.trim()) return;
    const q = chatInput.toLowerCase().trim();
    setChatMsgs(p => [...p, { from: "user", text: chatInput }]);
    setChatInput("");
    setTimeout(() => {
      if (q === "tutti" || q === "reset" || q === "all") {
        setFilter(CATALOG_ALL_KEY);
        setChatMsgs(p => [...p, { from: "agent", text: "Filter removed." }]);
        return;
      }
      const hit = families.find(f => f.toLowerCase().includes(q));
      if (hit) {
        setFilter(hit);
        setChatMsgs(p => [...p, { from: "agent", text: `Filter: ${hit}` }]);
      } else {
        const list = families.length ? families.join(", ") : (it ? "(nessuna categoria ancora)" : "(no categories yet)");
        setChatMsgs(p => [...p, { from: "agent", text: it ? `Categorie disponibili: ${list}` : `Available categories: ${list}` }]);
      }
    }, 400);
  };

  const filtered = rows.filter(p =>
    (filter === CATALOG_ALL_KEY || p.family_code === filter)
    && (!search
        || (p.name || "").toLowerCase().includes(search.toLowerCase())
        || (p.manufacturer || p.company_name || "").toLowerCase().includes(search.toLowerCase()))
  );

  // Click → fetch the full passport so PublicDPPView can render real data.
  const openCard = async (p) => {
    setSelectedDPP(p);
    setSelectedDetail(null);
    try {
      const r = await fetch(`/api/catalog/${p.id}`, { credentials: "include" });
      if (r.ok) setSelectedDetail(await r.json());
    } catch {}
  };
  const closeCard = () => { setSelectedDPP(null); setSelectedDetail(null); };

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: font, background: T.bgSoft, overflow: "hidden" }}>
      <Sidebar activePage="catalog" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 28px 40px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 800, color: T.navy, margin: 0 }}>{_("yourCatalog")}</h1>
              <p style={{ fontSize: 13, color: T.textSec, margin: "4px 0 0" }}>{filtered.length} {it?"schede disponibili":"sheets available"}</p>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <Btn small onClick={() => setChatOpen(!chatOpen)} style={{ border: `1px solid ${chatOpen ? T.accent : T.border}`, background: chatOpen ? T.accentSoft : T.bg, color: chatOpen ? T.accentDark : T.textSec }}><I d={ic.msg} size={13} color={chatOpen ? T.accentDark : T.textSec} /> {_("assistant")}</Btn>
            </div>
          </div>

          {/* Search + filters */}
          <div style={{ display: "flex", gap: 12, marginBottom: 20, alignItems: "center" }}>
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 8, padding: "9px 14px", borderRadius: 8, border: `1px solid ${T.border}`, background: T.bg }}>
              <I d={ic.search} size={16} color={T.textSec} />
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder={"Search by product or manufacturer…"} style={{ flex: 1, border: "none", outline: "none", fontSize: 13, background: "transparent", fontFamily: font }} />
            </div>
          </div>
          <div style={{ display: "flex", gap: 5, marginBottom: 20, flexWrap: "wrap" }}>
            {[CATALOG_ALL_KEY, ...families].map(ck => {
              const isAll = ck === CATALOG_ALL_KEY;
              const label = isAll ? _("all") : ck;
              const active = filter === ck;
              return (
                <button key={ck} onClick={() => setFilter(ck)} style={{ padding: "6px 14px", borderRadius: 6, fontSize: 12, fontWeight: active ? 700 : 500, cursor: "pointer", fontFamily: font, border: `1px solid ${active ? T.accent : T.border}`, background: active ? T.accentSoft : T.bg, color: active ? T.accentDark : T.textSec }}>{label}</button>
              );
            })}
          </div>

          {/* Product grid - cards are clickable, no Esplora button */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 14 }}>
            {filtered.map((p) => {
              const k = p.kpis || {};
              const gwp = k.gwp_total != null ? `${k.gwp_total} kgCO\u2082e/m\u00b2` : "\u2014";
              const recycled = k.recycled || "\u2014";
              const energy = k.energy_class || "\u2014";
              const mfr = p.manufacturer || p.company_name || "\u2014";
              return (
                <button key={p.id} onClick={() => openCard(p)} style={{ borderRadius: 12, border: `1px solid ${T.border}`, background: T.bg, overflow: "hidden", cursor: "pointer", fontFamily: font, textAlign: "left", padding: 0, display: "block", width: "100%", transition: "border-color 0.15s, box-shadow 0.15s" }} onMouseEnter={e=>{e.currentTarget.style.borderColor=T.accent;e.currentTarget.style.boxShadow=`0 0 0 1px ${T.accent}30`}} onMouseLeave={e=>{e.currentTarget.style.borderColor=T.border;e.currentTarget.style.boxShadow="none"}}>
                  <div style={{ display: "flex", gap: 14, padding: "16px 18px 10px", alignItems: "flex-start" }}>
                    <div style={{ width: 68, height: 68, borderRadius: 8, background: `linear-gradient(135deg, ${T.bgSoft}, ${T.accentSoft}40)`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, border: `1px solid ${T.borderLight}` }}>
                      <I d={ic.box} size={26} color={T.border} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 10, color: T.textSec, display: "flex", alignItems: "center", gap: 3, marginBottom: 2 }}><I d={ic.factory} size={9} color={T.textSec} />{mfr}</div>
                      <div style={{ fontSize: 15, fontWeight: 700, color: T.textDark, marginBottom: 5, lineHeight: 1.2 }}>{p.name || "\u2014"}</div>
                      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                        {p.is_own && <Badge color={T.amber} bg={T.amberSoft}>{_("yours")}</Badge>}
                        {p.family_code && <Badge color={T.textSec} bg={T.bgSoft}>{p.family_code}</Badge>}
                      </div>
                    </div>
                  </div>
                  <div style={{ padding: "0 18px 14px" }}>
                    {[["GWP Total", gwp], [_("recycled"), recycled], [_("energy"), energy]].map(([l, v], j) => (
                      <div key={j} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: j < 2 ? `1px solid ${T.borderLight}` : "none" }}>
                        <span style={{ fontSize: 12, color: T.textSec }}>{l}</span>
                        <span style={{ fontSize: 12, fontWeight: 700, color: T.textDark }}>{v}</span>
                      </div>
                    ))}
                  </div>
                </button>
              );
            })}
          </div>
          {loading && rows.length === 0 && (
            <div style={{ textAlign: "center", padding: 40, color: T.textSec }}>{it ? "Caricamento\u2026" : "Loading\u2026"}</div>
          )}
          {!loading && rows.length === 0 && (
            <div style={{ textAlign: "center", padding: 40, color: T.textSec }}>
              {it ? "Nessun passaporto pubblicato ancora." : "No published passports yet."}
            </div>
          )}
          {!loading && rows.length > 0 && filtered.length === 0 && (
            <div style={{ textAlign: "center", padding: 40, color: T.textSec }}>{_("noResults")}</div>
          )}
        </div>

        {/* Chat assistant */}
        {chatOpen && (
          <div style={{ width: 340, borderLeft: `1px solid ${T.border}`, background: T.bg, display: "flex", flexDirection: "column", flexShrink: 0 }}>
            <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 26, height: 26, borderRadius: "50%", background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.msg} size={12} color={T.accent} /></div>
                <div><div style={{ fontSize: 12, fontWeight: 700, color: T.textDark }}>{it?"Assistente Catalogo":"Catalog Assistant"}</div><div style={{ fontSize: 9, color: T.accent, fontWeight: 600 }}>{it?"Attivo":"Active"}</div></div>
              </div>
              <button onClick={() => setChatOpen(false)} style={{ background: "none", border: "none", cursor: "pointer", padding: 2 }}><I d={ic.x} size={16} color={T.textSec} /></button>
            </div>
            <div style={{ flex: 1, overflowY: "auto", padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
              {chatMsgs.map((m, i) => (
                <div key={i} style={{ alignSelf: m.from === "user" ? "flex-end" : "flex-start", maxWidth: "88%", padding: "9px 13px", borderRadius: m.from === "user" ? "10px 10px 2px 10px" : "10px 10px 10px 2px", background: m.from === "user" ? T.navy : T.bgSoft, color: m.from === "user" ? T.text : T.textDark, fontSize: 12, lineHeight: 1.55, border: m.from === "agent" ? `1px solid ${T.border}` : "none" }}>{m.text}</div>
              ))}
            </div>
            <div style={{ padding: 10, borderTop: `1px solid ${T.border}` }}>
              <div style={{ display: "flex", gap: 6, padding: "8px 10px", borderRadius: 8, border: `1px solid ${T.border}` }}>
                <input value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => e.key === "Enter" && chatSend()} placeholder="Es. Mostrami isolanti classe A+…" style={{ flex: 1, border: "none", outline: "none", fontSize: 12, background: "transparent", fontFamily: font }} />
                <button onClick={chatSend} style={{ width: 26, height: 26, borderRadius: 6, background: T.accent, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.arrow} size={13} color={T.navy} /></button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* DPP Overlay Modal — passes the fetched real passport to PublicDPPView */}
      {selectedDPP && (
        <div style={{ position: "fixed", inset: 0, zIndex: 1000, display: "flex", justifyContent: "center", alignItems: "stretch" }}>
          <div onClick={closeCard} style={{ position: "absolute", inset: 0, background: "rgba(15,23,41,0.6)", backdropFilter: "blur(4px)" }} />
          <div style={{ position: "relative", width: "100%", maxWidth: "min(780px, 92vw)", margin: "20px 0", background: T.bg, borderRadius: 16, overflow: "hidden", display: "flex", flexDirection: "column", boxShadow: "0 25px 60px rgba(0,0,0,0.3)", zIndex: 1001 }}>
            <button onClick={closeCard} style={{ position: "absolute", top: 12, right: 12, zIndex: 10, width: 32, height: 32, borderRadius: 8, background: "rgba(15,23,41,0.7)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.x} size={16} color="#F1F5F9" /></button>
            <div style={{ flex: 1, overflowY: "auto" }}>
              {selectedDetail
                ? <PublicDPPView L={L} dppData={selectedDetail} isSpecific />
                : <div style={{ padding: 60, textAlign: "center", color: T.textSec, fontSize: 13 }}>{it ? "Caricamento passaporto…" : "Loading passport…"}</div>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── SVG Charts ──────────────────────────────────────────
function GWPChart({ data }) {
  const _data = (data && data.length) ? data
    : [{l:"A1",v:2.1},{l:"A2",v:0.8},{l:"A3",v:1.3},{l:"A4",v:0.4},{l:"A5",v:0.3},{l:"C1",v:0.1},{l:"C2",v:0.2},{l:"C3",v:0.3},{l:"C4",v:0.5},{l:"D",v:-1.5}];
  const mx = Math.max(0.1, ..._data.map(d => Math.abs(d.v)));
  const h=120, w=Math.max(280, _data.length*28), bw=20, g=8;
  return (<svg width={w} height={h+30} style={{ display: "block" }}>
    <line x1={0} y1={h/2+5} x2={w} y2={h/2+5} stroke={T.border} strokeWidth={1} />
    {_data.map((d,i)=>{const x=i*(bw+g)+10;const bH=Math.abs(d.v)/mx*(h/2-5);const y=d.v>=0?h/2+5-bH:h/2+5;return(<g key={i}><rect x={x} y={y} width={bw} height={bH} rx={2} fill={d.v>=0?T.accent:T.accentDark} opacity={d.v>=0?0.7:1} /><text x={x+bw/2} y={h+16} textAnchor="middle" fontSize={8} fill={T.textSec} fontFamily={font}>{d.l}</text></g>);})}
  </svg>);
}
function DonutChart({ seg }) {
  const _seg = (seg && seg.length) ? seg : [{p:92,c:T.accent},{p:5,c:T.amber},{p:3,c:T.border}];
  const r=50,cx=60,cy=60,sw=14;let cum=0;
  return (<svg width={120} height={120}>
    {_seg.map((s,i)=>{const ci=2*Math.PI*r;const da=(s.p/100)*ci;const of2=-(cum/100)*ci;cum+=s.p;return <circle key={i} cx={cx} cy={cy} r={r} fill="none" stroke={s.c} strokeWidth={sw} strokeDasharray={`${da} ${ci-da}`} strokeDashoffset={of2} transform={`rotate(-90 ${cx} ${cy})`} />;})}
    <circle cx={cx} cy={cy} r={r-sw} fill="white" />
  </svg>);
}

// ─── APP VIEW (PUBLISHED / PREVIEW) ─────────────────────
function AppView({ onNavigate, L, product, onAddProjectDPP, onPublish }) {
  const _ = k => t(k, L?.lang);
  const it = L?.lang === "it";
  const [tab, setTab] = useState("panoramica");
  const [chatOpen, setChatOpen] = useState(false);
  const [published, setPublished] = useState(product?.status === "published");
  const [showEmbed, setShowEmbed] = useState(false);
  const [showCSV, setShowCSV] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [showPublicDPP, setShowPublicDPP] = useState(false);
  const [versions, setVersions] = useState([]);
  // Load real version history when the Versions tab is opened.
  useEffect(() => {
    if (tab === "versioni" && product?.id && !String(product.id).startsWith("prod-")) {
      fetch(`/api/products/${product.id}/versions`, { credentials: "include" })
        .then(r => r.ok ? r.json() : [])
        .then(v => { if (Array.isArray(v)) setVersions(v); })
        .catch(() => {});
    }
  }, [tab, product?.id]);

  const na = it ? "Non dichiarato" : "Not declared";

  // ── Passport resolution (real data with demo fallback) ──
  const pp = product?.dppData?.passport;
  const stats = product?.dppData?.stats;
  const hasAI = !!pp;
  // Resolve a passport field to its value, or the demo fallback when no AI data.
  const rv = (path, fallback) => {
    if (!hasAI) return fallback;
    const r = _ef(pp, path);
    return (r && r.v != null && r.v !== "") ? r.v : fallback;
  };
  const pname = rv("overview.product_info.product_name", "XPS Insulation Panel 100mm");
  const puid = rv("overview.product_info.uid", "DPP-20260115-a3f8c2d1");
  const pmfr = rv("overview.manufacturer.company_name", "Deeppy Construction Materials srl");
  const pctDone = Math.round(stats?.completeness ?? product?.completeness ?? 100);

  // ── Derived environmental + composition metrics from the real passport ──
  const _ev = (o, f) => { const x = o?.[f]; return (x && typeof x === "object") ? x.value : x; };
  const familyShort = hasAI
    ? ((rv("overview.product_info.product_family", "") || "").split(" - ")[0] || rv("overview.product_info.product_family_code", "") || _("insulation"))
    : _("insulation");
  // GWP per lifecycle stage (for the chart) + total
  const gwpStages = hasAI ? (pp?.lifecycle?.stages || [])
    .map(s => ({ l: s.stage_code || "?", v: Number(_ev(s, "gwp_total")) || 0 }))
    .filter(d => d.v !== 0) : [];
  const gwpTotal = gwpStages.reduce((a, d) => a + d.v, 0);
  // Recycled content from a performance value
  const recycledVal = hasAI ? (() => {
    const v = (pp?.performance?.values || []).find(x => /recycl|riciclat/i.test(x.property_name || ""));
    const raw = v ? _ev(v, "value") : null;
    return raw != null && raw !== "" ? `${raw}${String(raw).includes("%") ? "" : "%"}` : null;
  })() : "15%";
  // Composition donut segments from materials (% or quantity-derived)
  const donutSeg = hasAI ? (() => {
    const rows = (pp?.composition?.materials || []).map(m => ({
      name: _ev(m, "description") || "—",
      pct: Number(_ev(m, "percentage")) || 0,
      qty: Number(_ev(m, "quantity_per_product")) || 0,
    }));
    let withPct = rows.filter(r => r.pct > 0);
    if (!withPct.length) {
      const tot = rows.reduce((a, r) => a + r.qty, 0);
      if (tot > 0) withPct = rows.filter(r => r.qty > 0).map(r => ({ ...r, pct: r.qty / tot * 100 }));
    }
    if (!withPct.length) return null;
    withPct.sort((a, b) => b.pct - a.pct);
    const colors = [T.accent, T.amber, "#3B82F6", T.border];
    const top = withPct.slice(0, 3).map((r, i) => ({ p: Math.round(r.pct), c: colors[i], name: r.name }));
    const otherPct = withPct.slice(3).reduce((a, r) => a + r.pct, 0);
    if (otherPct > 0.5) top.push({ p: Math.round(otherPct), c: T.border, name: _("insulation") && "Other" });
    return top;
  })() : null;
  const generatePDF = () => {
    const qrUrl = `https://deeppy.eu/dpp/${puid}`;
    // Generate QR code as SVG using simple QR pattern (placeholder - real impl uses qrcode lib)
    const qrSvg = `<svg viewBox="0 0 100 100" width="120" height="120" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="white" rx="4"/><rect x="5" y="5" width="25" height="25" rx="2" fill="#0F1729"/><rect x="8" y="8" width="19" height="19" rx="1" fill="white"/><rect x="11" y="11" width="13" height="13" rx="1" fill="#0F1729"/><rect x="70" y="5" width="25" height="25" rx="2" fill="#0F1729"/><rect x="73" y="8" width="19" height="19" rx="1" fill="white"/><rect x="76" y="11" width="13" height="13" rx="1" fill="#0F1729"/><rect x="5" y="70" width="25" height="25" rx="2" fill="#0F1729"/><rect x="8" y="73" width="19" height="19" rx="1" fill="white"/><rect x="11" y="76" width="13" height="13" rx="1" fill="#0F1729"/><rect x="35" y="5" width="5" height="5" fill="#0F1729"/><rect x="45" y="5" width="5" height="5" fill="#0F1729"/><rect x="55" y="5" width="5" height="5" fill="#0F1729"/><rect x="35" y="15" width="5" height="5" fill="#0F1729"/><rect x="50" y="15" width="5" height="5" fill="#0F1729"/><rect x="60" y="15" width="5" height="5" fill="#0F1729"/><rect x="35" y="25" width="5" height="5" fill="#0F1729"/><rect x="45" y="25" width="5" height="5" fill="#0F1729"/><rect x="55" y="25" width="5" height="5" fill="#0F1729"/><rect x="5" y="35" width="5" height="5" fill="#0F1729"/><rect x="15" y="35" width="5" height="5" fill="#0F1729"/><rect x="25" y="35" width="5" height="5" fill="#0F1729"/><rect x="40" y="40" width="20" height="20" rx="4" fill="#34D399"/><text x="50" y="54" text-anchor="middle" font-size="10" font-weight="800" fill="#0F1729" font-family="Inter,sans-serif">DPP</text><rect x="70" y="35" width="5" height="5" fill="#0F1729"/><rect x="80" y="35" width="5" height="5" fill="#0F1729"/><rect x="90" y="35" width="5" height="5" fill="#0F1729"/><rect x="5" y="45" width="5" height="5" fill="#0F1729"/><rect x="20" y="45" width="5" height="5" fill="#0F1729"/><rect x="70" y="50" width="5" height="5" fill="#0F1729"/><rect x="85" y="50" width="5" height="5" fill="#0F1729"/><rect x="5" y="55" width="5" height="5" fill="#0F1729"/><rect x="15" y="55" width="5" height="5" fill="#0F1729"/><rect x="25" y="55" width="5" height="5" fill="#0F1729"/><rect x="70" y="65" width="5" height="5" fill="#0F1729"/><rect x="80" y="65" width="5" height="5" fill="#0F1729"/><rect x="90" y="65" width="5" height="5" fill="#0F1729"/><rect x="35" y="70" width="5" height="5" fill="#0F1729"/><rect x="45" y="75" width="5" height="5" fill="#0F1729"/><rect x="55" y="70" width="5" height="5" fill="#0F1729"/><rect x="70" y="75" width="5" height="5" fill="#0F1729"/><rect x="80" y="80" width="5" height="5" fill="#0F1729"/><rect x="90" y="75" width="5" height="5" fill="#0F1729"/><rect x="35" y="85" width="5" height="5" fill="#0F1729"/><rect x="50" y="90" width="5" height="5" fill="#0F1729"/><rect x="70" y="90" width="5" height="5" fill="#0F1729"/><rect x="85" y="85" width="5" height="5" fill="#0F1729"/></svg>`;

    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>DPP Summary</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;color:#1E293B;font-size:12px;line-height:1.5}
.page{max-width:700px;margin:0 auto;padding:40px}
.header{display:flex;justify-content:space-between;align-items:center;padding-bottom:20px;border-bottom:3px solid #34D399;margin-bottom:28px}
.logo-area{display:flex;align-items:center;gap:10px}
.logo-area img{height:36px;width:36px;border-radius:8px;object-fit:cover}
.logo-text{font-size:22px;font-weight:800;letter-spacing:-0.02em;color:#0F1729}
.logo-text b{color:#34D399}
.badge{display:inline-block;padding:3px 10px;border-radius:4px;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;background:#D1FAE5;color:#059669;margin-left:10px}
.product-name{font-size:26px;font-weight:800;color:#0F1729;margin:0 0 4px}
.subtitle{font-size:13px;color:#64748B;margin-bottom:28px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px}
.section-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#059669;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #D1FAE5}
.row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F1F5F9;font-size:11.5px}
.row .label{color:#64748B}
.row .value{font-weight:600;text-align:right}
.qr-section{display:flex;align-items:center;gap:24px;padding:24px;border-radius:12px;background:#F8FAFC;border:1px solid #E2E8F0;margin-top:28px}
.qr-text h3{font-size:14px;font-weight:700;color:#0F1729;margin-bottom:4px}
.qr-text p{font-size:11px;color:#64748B;line-height:1.5}
.qr-text a{color:#059669;font-weight:600;font-size:10px;word-break:break-all}
.footer{margin-top:28px;padding-top:12px;border-top:2px solid #D1FAE5;display:flex;justify-content:space-between;font-size:9px;color:#94A3B8}
.na{color:#94A3B8;font-style:italic}
@media print{body{padding:0}.page{padding:20px 28px}}
</style></head><body><div class="page">
<div class="header">
  <div class="logo-area"><img src="${LOGO_SRC}" /><span class="logo-text">Dee<b>PP</b>y</span><span class="badge">Digital Product Passport</span></div>
  <div style="text-align:right;font-size:10px;color:#64748B">${it?"Generato":"Generated"}: ${new Date().toLocaleDateString(it?"it-IT":"en-GB")}<br>v2.3</div>
</div>
<h1 class="product-name">${pname}</h1>
<div class="subtitle">${pmfr} — ${rv("overview.product_info.product_family", it?"Isolanti termici":"Thermal insulation")}</div>
<div class="grid">
  <div>
    <div class="section-title">${it?"Prodotto":"Product"}</div>
    <div class="row"><span class="label">UID</span><span class="value">${puid}</span></div>
    <div class="row"><span class="label">${it?"Categoria":"Category"}</span><span class="value">${rv("overview.product_info.product_family", it?"Isolamento termico":"Thermal insulation")}</span></div>
    <div class="row"><span class="label">${it?"Dimensioni":"Dimensions"}</span><span class="value">${rv("overview.product_info.standard_dimension", "1250 × 600 × 100 mm")}</span></div>
    <div class="row"><span class="label">${it?"Peso":"Weight"}</span><span class="value">${rv("overview.product_info.weight", "3.5 kg/m²")}</span></div>
    <div class="row"><span class="label">${it?"Unità funzionale":"Functional unit"}</span><span class="value">${rv("overview.product_info.functional_unit", "1 m² × 100mm")}</span></div>
  </div>
  <div>
    <div class="section-title">${it?"Produttore":"Manufacturer"}</div>
    <div class="row"><span class="label">${it?"Azienda":"Company"}</span><span class="value">${pmfr}</span></div>
    <div class="row"><span class="label">${it?"Sede":"HQ"}</span><span class="value">${rv("overview.manufacturer.address", "Via Emilia 42, Rimini (RN)")}</span></div>
    <div class="row"><span class="label">${it?"Stabilimento":"Plant"}</span><span class="value">${rv("overview.manufacturer.manufacturing_site", "Novara, Via Industria 8")}</span></div>
    <div class="row"><span class="label">Email</span><span class="value">${rv("overview.manufacturer.email", "—")}</span></div>
  </div>
</div>
<div class="grid">
  <div>
    <div class="section-title">${it?"Prestazioni chiave":"Key Performance"}</div>
    <div class="row"><span class="label">λ</span><span class="value">0.034 W/(m·K)</span></div>
    <div class="row"><span class="label">${it?"Resistenza termica":"Thermal resistance"}</span><span class="value">2.94 m²·K/W</span></div>
    <div class="row"><span class="label">${it?"Classe fuoco":"Fire class"}</span><span class="value">E (Euroclass)</span></div>
    <div class="row"><span class="label">GWP (A1-A3)</span><span class="value">3.4 kg CO₂ eq/m²</span></div>
  </div>
  <div>
    <div class="section-title">${it?"Conformità":"Compliance"}</div>
    <div class="row"><span class="label">CE</span><span class="value">CE-0432-CPR-2024</span></div>
    <div class="row"><span class="label">DoP</span><span class="value">DoP-XPS100-2024-R3</span></div>
    <div class="row"><span class="label">EPD</span><span class="value">EPD-EDT-2024-0847</span></div>
    <div class="row"><span class="label">CAM</span><span class="value">DM 23/06/2022</span></div>
  </div>
</div>
<div class="section-title">${it?"Composizione (BOM)":"Composition (BOM)"}</div>
<div class="row"><span class="label" style="font-weight:600;color:#0F1729">${pname}</span><span class="value">100%</span></div>
<div class="row" style="padding-left:16px"><span class="label">${it?"Polistirene espanso estruso":"Extruded polystyrene (XPS)"}</span><span class="value">94.5%</span></div>
<div class="row" style="padding-left:32px"><span class="label">${it?"Granuli XPS vergini":"Virgin XPS granules"} (UE)</span><span class="value">82.5%</span></div>
<div class="row" style="padding-left:32px"><span class="label">${it?"Granuli XPS riciclati":"Recycled XPS granules"} (UE) ♻</span><span class="value">12%</span></div>
<div class="row" style="padding-left:16px"><span class="label">${it?"Agente espandente (CO₂)":"Blowing agent (CO₂)"} (UE)</span><span class="value">3.2%</span></div>
<div class="row" style="padding-left:16px"><span class="label">${it?"Ritardanti di fiamma":"Flame retardants"} (UE/DE)</span><span class="value">1.8%</span></div>
<div class="row" style="padding-left:16px"><span class="label">${it?"Colorante":"Colorant"} (UE)</span><span class="value">0.5%</span></div>

<div class="section-title">${it?"Catena di Fornitura":"Supply Chain"}</div>
<div class="row"><span class="label" style="font-weight:600">${it?"Operatore":"Operator"}</span><span class="value" style="font-weight:600">${it?"Localizzazione":"Location"}</span></div>
<div class="row"><span class="label">Levery srl (${it?"Produttore":"Manufacturer"})</span><span class="value">Rimini, IT</span></div>
<div class="row"><span class="label">Arpa Industriale</span><span class="value">Bra, IT</span></div>
<div class="row"><span class="label">Rockwool Italia</span><span class="value">Porcari, IT</span></div>
<div class="row"><span class="label">Metra SpA</span><span class="value">Rodengo-Saiano, IT</span></div>
<div class="row"><span class="label">BASF SE (${it?"Additivi":"Additives"})</span><span class="value">Ludwigshafen, DE</span></div>
<div style="margin:10px 0;padding:8px 12px;border-radius:6px;background:#D1FAE5;font-size:10px;color:#059669;font-weight:600">✔ ${it?"100% catena di fornitura UE — Conforme ESPR Art. 9":"100% EU supply chain — ESPR Art. 9 compliant"}</div>

<div class="qr-section">
  ${qrSvg}
  <div class="qr-text">
    <h3>${it?"Passaporto Digitale Completo":"Full Digital Passport"}</h3>
    <p>${it?"Scansiona il QR code o visita il link per accedere al passaporto digitale aggiornato con tutti i dati tecnici, ambientali, documenti e cronologia versioni.":"Scan the QR code or visit the link to access the up-to-date digital passport with all technical, environmental data, documents and version history."}</p>
    <a href="${qrUrl}">${qrUrl}</a>
  </div>
</div>
<div class="footer">
  <span class="logo-text" style="font-size:11px">Dee<b>PP</b>y</span>
  <span>${it?"Conforme al Regolamento ESPR (UE) 2024/1781":"Compliant with ESPR Regulation (EU) 2024/1781"} — deeppy.eu</span>
</div>
</div></body></html>`;

    const blob = new Blob([html], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "DPP-XPS100-Summary.html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const csvData = (() => {
    const h = [it?"Famiglia Dati":"Data Family", it?"Dato":"Data", "Required/Optional", it?"Dato Dettagliato":"Detailed Data", it?"Dato Specifico":"Specific data", it?"Specifica Tecnica":"Technical spec", it?"Unità":"Unit", it?"Valore":"Value"];
    const R = "Required", O = "Optional";
    const rows = [
      // General Product Information
      ["General Product Information","Product Name",R,"","","","","-",pname],
      ["","Unique Product Identifier (UID)",R,"","","","","-",puid],
      ["","Item type",R,"","","","","-",rv("overview.product_info.item_type","Product")],
      ["","Product category",R,"","","","","-",rv("overview.product_info.product_family","Thermal insulation products")],
      ["","Batch Number (BN) / Serial Number (SN)",O,"","","","","-",rv("overview.product_info.batch_number","")],
      ["","Global Trade Identification Number (GTIN)",O,"","","","","-",rv("overview.product_info.gtin","")],
      ["","Product image",O,"","","","","-","XPS-100mm.jpg"],
      ["","Product description",O,"","","","","-",rv("overview.product_info.product_description",it?"Pannello isolante in XPS ad alta densità per isolamento termico":"High-density XPS insulation panel for thermal insulation")],
      ["","Company info",R,"","","","","-",`${pmfr} — ${rv("overview.manufacturer.address","Via Emilia 42, Rimini")} — ${rv("overview.manufacturer.website","www.deeppy-materials.it")}`],
      ["","Company manufacturing site",R,"","","","","-",rv("overview.manufacturer.manufacturing_site","Stabilimento Novara, Via Industria 8, 28100 Novara")],
      ["","Manufacturing date",O,"","","","","-",rv("overview.product_info.production_period","")],
      ["","Contact information",R,"","","","","-",rv("overview.manufacturer.email","a.pracucci@levery.it")],
      ["","Sale type",O,"","","","","-","Direct sales, Retailers"],
      ["","Functional unit",R,"","","","","-","1 m² thickness 100mm"],
      ["","Standard dimension (WxDxH)",O,"","","","","-","1250 × 600 × 100 mm"],
      ["","Weight",O,"","","","","-","3.5 kg/m²"],
      ["","Sourcing composition and supplier",R,"Component/Raw Material #1","","","","-","Polystyrene (granule) — 92% — EU origin"],
      ["","",R,"Component/Raw Material #2","","","","-","Flame retardant additives — 5% — HBCD-free"],
      ["","",R,"Component/Raw Material #3","","","","-","Blowing agent (CO₂/HFC) — 3% — CO₂-based"],
      // Declaration of Performance & Conformity
      ["Declaration of Performance & Conformity","Declaration of Performance (DoP)",O,"Reference standard #1","","","","-","DoP N. XPS-100-2026-001 — EN 13164:2012+A1:2015"],
      ["","Declaration of Conformity (DoC)",O,"","","","","",""],
      ["","CE Marking",O,"","","","","-",it?"Conforme — Certificato CE n. 0123-CPR-2024":"Compliant — CE Certificate n. 0123-CPR-2024"],
      ["","Quality control",O,"","","","","-","FPC Certificate n. 0123-CPR-FPC"],
      ["","Safety Information",O,"Does it contain any CMRs candidates? Y/N","","","","-","No"],
      ["","",O,"Does it contain any SVHCs candidates? Y/N","","","","-","No"],
      ["","",O,"Does it contain pentane? Y/N","","","","-",it?"Sì (agente espandente, < 2%)":"Yes (blowing agent, < 2%)"],
      ["","",O,"Does it contain PFAS? Y/N","","","","-","No"],
      ["","",O,"Does it have flame retardancy? Y/N","","","","-",it?"Sì (HBCD-free, polimerico)":"Yes (HBCD-free, polymeric)"],
      ["","",O,"Does it comply with RoHS? Y/N","","","","-",it?"Sì":"Yes"],
      ["","",O,"Does it comply with Child labor regulation? Y/N","","","","-",it?"Sì":"Yes"],
      ["","Other declaration",O,"","","","","",""],
      // Labeling
      ["Labeling","Product certifications",O,"Certification #1","","","","-","EPD-XPS100-2025 — EPD Hub"],
      ["","Company certification",O,"Certification #1","","","","-","ISO 9001:2015 — QMS-2024-0456"],
      ["","",O,"Certification #2","","","","-","ISO 14001:2015 — EMS-2024-0789"],
      // Technical Documentation — Guidelines
      ["Technical Documentation","Guideline",O,"Method Statement for Installation","","","","",""],
      ["","",O,"Method Statement for Maintenance and Repair","","","","",""],
      ["","",O,"Method Statement for Replacement/refurbishment","","","","",""],
      ["","Drawings",O,"2D model","","","","",""],
      ["","",O,"3D model","","","","",""],
      // [A3] Performance — Required
      ["","Performance",R,"Properties","Mechanical properties","Compressive strength","Pa","300 kPa"],
      ["","",R,"","","Tensile strength","Pa","≥ 200 kPa"],
      ["","",R,"","","Flexural strength","Pa","≥ 500 kPa"],
      ["","",R,"","","Elasticity modulus","Pa","25 MPa"],
      ["","",R,"","","Impact resistance","Pa",it?"Classe 2":"Class 2"],
      ["","",R,"","Thermal Properties","Thermal conductivity","W/mK","0.034 W/(m·K)"],
      ["","",R,"","","Fire resistance class","-","E (EN 13501-1)"],
      ["","",R,"","","Expansion coefficient","um/m/°C","0.07 mm/(m·K)"],
      ["","",R,"","Acoustic Properties","Sound absorption coefficient","%",""],
      ["","",R,"","","Sound insulation rating","dB",""],
      ["","",R,"","Moisture & Water Resistance","Water absorption","%","≤ 0.7% vol"],
      ["","",R,"","","Permeability to water vapor","perms","80-250"],
      ["","",R,"","","Resistance to freeze-thaw cycles","-",it?"Conforme":"Compliant"],
      ["","",R,"","Durability & Environmental Resistance","UV resistance","w/sqm",it?"Protezione richiesta":"Protection required"],
      ["","",R,"","","Corrosion resistance (for metallic elements)","mpy","N/A"],
      ["","",R,"","","Resistance to chemicals or biological agents","mg/L",it?"Resistente a soluzioni saline, alcali deboli":"Resistant to saline solutions, weak alkalis"],
      // [A1][A2] Production / suppliers
      ["","[A1] [A2] Production / suppliers",O,"Material #1","Material/product description","","","-","Polystyrene granule — 92%"],
      ["","",O,"","Material/product impact","Emission","","-","GWP A1: 3.21 kg CO₂eq/FU"],
      ["","",O,"","Production site","","","-","EU"],
      ["","",O,"","Transport type","","","-","Road (truck 16-32t)"],
      ["","",O,"","Material Origin","","","-","Virgin (100%)"],
      // [A3] Design & Manufacturing
      ["","[A3] Design & Manufacturing",O,"Manufacturing process","","","","-",it?"Estrusione continua → taglio → confezionamento":"Continuous extrusion → cutting → packaging"],
      ["","",O,"Data","","","","-","Energy: 12.4 MJ/FU — Waste: < 2%"],
      // [A4] Transportation
      ["","[A4] Transportation",O,"Data","","","","-","Road (truck 16-32t) — 100 km"],
      ["","",R,"Destination","","","","",""],
      // [A5] Construction & Installation
      ["","[A5] Construction & Installation",O,"Method Statement for Installation","","","","",""],
      ["","",O,"Installation company","","","","",""],
      // [B1] Use
      ["","[B1] Use",O,"Intended use","","","","-",it?"Isolamento termico pareti, coperture, pavimenti":"Thermal insulation for walls, roofs, floors"],
      // [B2-B3] Maintenance
      ["","[B2-3] Maintenance & Repair",O,"Method Statement for Maintenance","","","","",""],
      // [B4-B5] Replacement
      ["","[B4] [B5] Replacement - Refurbishment",O,"Method Statement for Replacement","","","","",""],
      // [B6-B7] Operational
      ["","[B6] [B7] Operational energy/water use",O,"Historical data","","","","-","N/A (passive product)"],
      // [C1] Deconstruction
      ["","[C1] Deconstruction",O,"Method Statement for Dismantling","","","","",""],
      // [C2] Transport
      ["","[C2] Transport",O,"Type","","","","-","Road"],
      ["","",O,"Distance","","","","-","50 km (scenario)"],
      // [C3-C4] Waste processing
      ["","[C3] [C4] Waste processing",O,"EoL instruction","","","","-",it?"Riciclaggio meccanico o recupero energetico":"Mechanical recycling or energy recovery"],
      // Other
      ["Other documentation required","","O","","","","","",""],
    ];
    // Filter: Required always shown (N/A if empty), Optional only if value present
    const na = it ? "Non disponibile" : "Not available";
    const filtered = rows.filter(r => {
      const req = r[2];
      const val = r[r.length - 1];
      if (req === R) return true;
      if (req === O && val && val.trim() !== "") return true;
      return false;
    }).map(r => {
      const val = r[r.length - 1];
      const reqOpt = r[2];
      if (reqOpt === R && (!val || val.trim() === "")) r[r.length - 1] = na;
      return r;
    });
    return [h, ...filtered];
  })();

  const downloadCSV = () => {
    const esc = v => '"' + String(v).replace(/"/g, '""') + '"';
    const csv = csvData.map(r => r.map(esc).join(",")).join("\n");
    const bom = "\uFEFF";
    const b = new Blob([bom + csv], {type:"text/csv;charset=utf-8"});
    const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = "DPP-XPS100.csv"; document.body.appendChild(a); a.click(); document.body.removeChild(a);
  };

  const Row = ({ l, v, tags }) => (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 16px", borderBottom: `1px solid ${T.borderLight}` }}>
      <span style={{ fontSize: 13, color: T.textSec }}>{l}</span>
      {tags ? <div style={{ display: "flex", gap: 4 }}>{tags.map((t,i)=><Badge key={i} color={T.textSec} bg={T.bgSoft}>{t}</Badge>)}</div> : <span style={{ fontSize: 14, fontWeight: 600, color: T.textDark }}>{v}</span>}
    </div>
  );
  const Card = ({ title, iconD, children }) => (
    <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden" }}>
      <div style={{ padding: "14px 18px", borderBottom: `1px solid ${T.borderLight}`, display: "flex", alignItems: "center", gap: 8 }}><I d={iconD} size={16} color={T.accentDark} /><span style={{ fontSize: 15, fontWeight: 700, color: T.textDark }}>{title}</span></div>
      {children}
    </div>);
  // ─── Multi-level DPP navigation (Model / Batch / Item) ───
  const [dppLevel, setDppLevel] = useState("model"); // "model" | "batch" | "item"
  const [selectedBatchId, setSelectedBatchId] = useState(null);
  const [selectedItemId, setSelectedItemId] = useState(null);

  // Demo data showing the Model → Batch → Item hierarchy.
  // Replaced by real product/batch/item data when persistence is added.
  const perenneData = {
    batches: [
      { id: "b1", lot: "PR-2026-015", site: it?"Stab. Treviso":"Treviso plant", date: "15 Mar 2026", pct: 95, items: [
        { id: "i1", sn: "#PERENNE-001", dims: "1200×1500mm", weight: "38kg", dest: "Villa Marchetti", date: "16 Mar 2026" },
        { id: "i2", sn: "#PERENNE-002", dims: "900×2100mm", weight: "42kg", dest: "Villa Marchetti", date: "16 Mar 2026" },
        { id: "i3", sn: "#PERENNE-003", dims: "1400×1200mm", weight: "35kg", dest: "Villa Marchetti", date: "17 Mar 2026" },
      ]},
      { id: "b2", lot: "PR-2026-012", site: it?"Stab. Treviso":"Treviso plant", date: "5 Mar 2026", pct: 100, items: [
        { id: "i4", sn: "#PERENNE-004", dims: "1500×1500mm", weight: "44kg", dest: "Edificio Verde", date: "6 Mar 2026" },
        { id: "i5", sn: "#PERENNE-005", dims: "1200×2100mm", weight: "40kg", dest: "Edificio Verde", date: "6 Mar 2026" },
      ]},
      { id: "b3", lot: "PR-2026-008", site: it?"Stab. Padova":"Padova plant", date: "20 Feb 2026", pct: 100, items: [
        { id: "i6", sn: "#PERENNE-006", dims: "800×1200mm", weight: "28kg", dest: "Residenza Sole", date: "21 Feb 2026" },
        { id: "i7", sn: "#PERENNE-007", dims: "1000×2400mm", weight: "52kg", dest: "Residenza Sole", date: "21 Feb 2026" },
        { id: "i8", sn: "#PERENNE-008", dims: "600×900mm", weight: "18kg", dest: "Residenza Sole", date: "22 Feb 2026" },
      ]},
      { id: "b4", lot: "PR-2026-003", site: it?"Stab. Treviso":"Treviso plant", date: "10 Feb 2026", pct: 100, items: [
        { id: "i9", sn: "#PERENNE-009", dims: "1200×1500mm", weight: "38kg", dest: "Hotel Adriatico", date: "11 Feb 2026" },
        { id: "i10", sn: "#PERENNE-010", dims: "1200×1500mm", weight: "38kg", dest: "Hotel Adriatico", date: "11 Feb 2026" },
      ]},
      { id: "b5", lot: "PR-2025-098", site: it?"Stab. Padova":"Padova plant", date: "15 Dic 2025", pct: 100, items: [
        { id: "i11", sn: "#PERENNE-011", dims: "1000×1800mm", weight: "36kg", dest: "Palazzo Rossi", date: "16 Dic 2025" },
      ]},
    ]
  };
  const allItems = perenneData.batches.flatMap(b => b.items.map(i => ({ ...i, batchLot: b.lot, batchId: b.id })));
  const currentBatch = perenneData.batches.find(b => b.id === selectedBatchId);
  const currentItem = allItems.find(i => i.id === selectedItemId);
  const levelLabel = dppLevel === "model" ? "Model" : dppLevel === "batch" ? "Batch" : "Item";

  const prodTabs = [{key:"panoramica",label:_("overview"),d:ic.chart},{key:"composizione",label:_("composition"),d:ic.layers},{key:"prestazioni",label:_("performance"),d:ic.bolt},{key:"conformita",label:_("compliance"),d:ic.shield},{key:"lifecycle",label:_("lifecycle"),d:ic.clock}];
  // Management tabs depend on DPP level:
  // - Model: Batch + Item (can drill into either)
  // - Batch: Item only
  // - Item: no further management
  const mgmtTabs = dppLevel === "model"
    ? [{key:"batch",label:"Batch",d:ic.layers},{key:"item",label:"Item",d:ic.box},{key:"documenti",label:_("documents"),d:ic.file},{key:"versioni",label:it?"Versioni":"Versions",d:ic.clock}]
    : dppLevel === "batch"
    ? [{key:"item",label:"Item",d:ic.box},{key:"documenti",label:_("documents"),d:ic.file},{key:"versioni",label:it?"Versioni":"Versions",d:ic.clock}]
    : [{key:"documenti",label:_("documents"),d:ic.file},{key:"versioni",label:it?"Versioni":"Versions",d:ic.clock}];
  const ptabs = [...prodTabs, ...mgmtTabs];
  const [projBatch, setProjBatch] = useState("");
  const [projSite, setProjSite] = useState("");
  const [projRef, setProjRef] = useState("");
  const [projDims, setProjDims] = useState("");
  const [projWeight, setProjWeight] = useState("");
  const [projNotes, setProjNotes] = useState("");
  const [projCreated, setProjCreated] = useState(false);
  const [showManual, setShowManual] = useState(false);
  const [selectedSpec, setSelectedSpec] = useState(null);
  const [specFilter, setSpecFilter] = useState("");
  const specDPPs = (product?.projectDPPs || []).map(p => ({
    id: p.id,
    batch: p.batch || "",
    site: p.site || "",
    ref: p.ref || "",
    dims: p.dims || "",
    weight: p.weight || "",
    date: p.createdAt ? new Date(p.createdAt).toLocaleDateString(L?.lang === "it" ? "it-IT" : "en-US", { day: "numeric", month: "short", year: "numeric" }) : "",
    pct: 100,
  }));
  const filteredSpecs = specDPPs.filter(s => !specFilter || s.batch.toLowerCase().includes(specFilter.toLowerCase()) || (s.ref && s.ref.toLowerCase().includes(specFilter.toLowerCase())));

  const renderTab = () => {
    switch(tab){
    case "panoramica": return (<>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <Card title={_("envImpact")} iconD={ic.chart}><div style={{ padding: "16px 18px" }}><div style={{ fontSize: 12, color: T.textSec, marginBottom: 12 }}>Global Warming Potential by lifecycle stage</div>{(!hasAI || gwpStages.length) ? <><GWPChart data={hasAI ? gwpStages : undefined} /><div style={{ display: "flex", justifyContent: "space-between", marginTop: 12 }}><span style={{ fontSize: 12, color: T.textSec }}>Total GWP{hasAI ? "" : " (A1-D)"}</span><span style={{ fontSize: 16, fontWeight: 800, color: T.accentDark }}>{hasAI ? `${gwpTotal.toFixed(2)} kg CO₂eq` : "5.5 kg CO₂eq/m²"}</span></div></> : <div style={{ fontSize: 12, color: T.textSec, fontStyle: "italic", padding: "20px 0" }}>{it?"Nessun dato LCA estratto.":"No LCA data extracted."}</div>}</div></Card>
        <Card title={_("matComposition")} iconD={ic.layers}>{(!hasAI || donutSeg) ? <div style={{ padding: "16px 18px", display: "flex", alignItems: "center", gap: 20 }}><DonutChart seg={hasAI ? donutSeg : undefined} /><div>{(hasAI ? donutSeg : [{name:"XPS",p:92,c:T.accent},{name:"Additives",p:5,c:T.amber},{name:"Other",p:3,c:T.border}]).map((s,i)=>(<div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ width: 10, height: 10, borderRadius: "50%", background: s.c }} /><span style={{ fontSize: 13, color: T.textDark, maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.name}</span><span style={{ fontSize: 13, fontWeight: 700, color: T.accentDark }}>{s.p}%</span></div>))}</div></div> : <div style={{ padding: "16px 18px", fontSize: 12, color: T.textSec, fontStyle: "italic" }}>{it?"Nessuna composizione con percentuali.":"No composition percentages available."}</div>}</Card>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <Card title={_("manufacturer")} iconD={ic.factory}><Row l={_("fCompany")} v={pmfr} /><Row l={_("fLegalHQ")} v={rv("overview.manufacturer.address", "Via Emilia 42, 47921 Rimini (RN)")} /><Row l={_("fProdSite")} v={rv("overview.manufacturer.manufacturing_site", "Novara Plant, Via Industria 8")} /><Row l={it?"Sito web":"Website"} v={rv("overview.manufacturer.website", na)} /><Row l="Email" v={rv("overview.manufacturer.email", na)} /><Row l={it?"Telefono":"Phone"} v={rv("overview.manufacturer.phone", na)} /></Card>
        <Card title={_("product")} iconD={ic.box}><Row l={_("fProductName")} v={pname} /><Row l="UID" v={puid} /><Row l={_("fCprCategory")} v={rv("overview.product_info.product_family", it?"Prodotti per isolamento termico":"Thermal insulation products")} /><Row l={_("fFuncUnit")} v={rv("overview.product_info.functional_unit", it?"1 m² spessore 100mm":"1 m² thickness 100mm")} /><Row l={it?"Descrizione":"Description"} v={rv("overview.product_info.product_description", it?"Pannello isolante XPS ad alta densità":"High-density XPS insulation panel")} /><Row l={_("fDimensions")} v={rv("overview.product_info.standard_dimension", "1250 × 600 × 100 mm")} /><Row l={_("fWeight")} v={rv("overview.product_info.weight", "3.5 kg/m²")} /><Row l={_("fIntendedUse")||(it?"Uso previsto":"Intended use")} v={rv("overview.product_info.intended_use", na)} /><Row l="GTIN/EAN" v={rv("overview.product_info.gtin", na)} /><Row l={it?"Lotto di produzione":"Production batch"} v={rv("overview.product_info.batch_number", na)} /></Card>
      </div>
      <SupplyMap dppData={product?.dppData} />
    </>);
    case "composizione": return (<ComponentiTab editMode={false} onNavigate={onNavigate} L={L} dppData={product?.dppData} />);
    case "prestazioni": {
      if (hasAI) {
        const vals = pp?.performance?.values || [];
        if (!vals.length) return <Card title={_("performance")} iconD={ic.bolt}><div style={{ padding: "16px 18px", fontSize: 13, color: T.textSec }}>{it?"Nessun dato prestazionale estratto.":"No performance data extracted."}</div></Card>;
        const cats = {};
        vals.forEach(v => { const c = v.category || "Other"; (cats[c] = cats[c] || []).push(v); });
        const catIcon = { Mechanical: ic.shield, Thermal: ic.thermo, Acoustic: ic.bolt, Fire: ic.bolt, Durability: ic.leaf, Environmental: ic.leaf, Other: ic.bolt };
        return <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {Object.entries(cats).map(([cat, items]) => (
            <Card key={cat} title={cat} iconD={catIcon[cat] || ic.bolt}>
              {items.map((v, i) => { const val = (v.value && typeof v.value === "object") ? v.value.value : v.value; return <Row key={i} l={v.property_name} v={`${val ?? ""}${v.unit ? " " + v.unit : ""}`.trim() || na} />; })}
            </Card>
          ))}
        </div>;
      }
      return (<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
      <Card title={_("mechPerf")} iconD={ic.shield}><Row l={_("fCompStrength")} v="300 kPa" /><Row l={_("fFlexStrength")} v="≥ 500 kPa" /><Row l={_("fTensStrength")} v="≥ 200 kPa" /><Row l={_("fElastMod")} v="25 MPa" /></Card>
      <Card title={_("thermPerf")} iconD={ic.thermo}><Row l={_("fThermCond")} v="0.034 W/(m·K)" /><Row l={_("fThermRes")} v="2.94 m²·K/W" /><Row l={_("fFireClass")} v="E (EN 13501-1)" /><Row l={_("fExpCoeff")} v="0.07 mm/(m·K)" /></Card>
      <Card title={_("moisture")} iconD={ic.droplet}><Row l={_("fWaterAbs")} v="≤ 0.7% vol" /><Row l={_("fVaporPerm")} v="80-250" /><Row l={_("fFreezeThaw")} v="Compliant" /></Card>
      <Card title={_("durability")} iconD={ic.leaf}><Row l={_("fUvRes")} v="Protection required" /><Row l={_("fChemRes")} v="Soluzioni saline, alcali deboli" /></Card>
    </div>);
    }
    case "conformita": return (<>
      <Card title={_("declarations")} iconD={ic.clip}><Row l="DoP" v={rv("compliance.dop_reference", "DoP N. XPS-100-2026-001")} /><Row l={_("fRefStandard")} v={rv("compliance.dop_standard", "EN 13164:2012+A1:2015")} /><Row l={_("fCeMark")} v={rv("compliance.ce_marking", L?.lang==="it"?"Conforme — Cert. 0123-CPR-2024":"Compliant — Cert. 0123-CPR-2024")} /><Row l={_("fQC")} v={rv("compliance.quality_control", "FPC Cert. 0123-CPR-FPC")} /></Card>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <Card title={_("prodSafety")} iconD={ic.shield}><Row l="CMR" v={rv("compliance.safety.contains_cmrs", "No")} /><Row l="SVHC" v={rv("compliance.safety.contains_svhcs", "No")} /><Row l={_("fPentane")} v={rv("compliance.safety.contains_pentane", it?"Sì (< 2%)":"Yes (< 2%)")} /><Row l="PFAS" v={rv("compliance.safety.contains_pfas", "No")} /><Row l={_("fFlameRet")} v={rv("compliance.safety.has_flame_retardancy", it?"Sì (polimerico)":"Yes (polymeric)")} /><Row l="RoHS" v={rv("compliance.safety.complies_rohs", "Compliant")} /><Row l={it?"Emissioni VOC?":"VOC emissions?"} v={rv("compliance.safety.produces_voc", "No")} /><Row l={it?"Metalli pesanti?":"Heavy metals?"} v={rv("compliance.safety.contains_heavy_metals", "No")} /><Row l={it?"Amianto?":"Asbestos?"} v={rv("compliance.safety.contains_asbestos", "No")} /><Row l={_("fChildLabor")} v={rv("compliance.safety.complies_child_labor", "Compliant")} /></Card>
        <Card title={_("prodCerts")} iconD={ic.check}>{(() => {
          if (!hasAI) return (<><Row l="EPD" v="EPD-XPS100-2025" /><Row l="ISO 9001" v="QMS-2024-0456" /><Row l="ISO 14001" v="EMS-2024-0789" /><Row l="CAM" v={it?"Conforme DM 23/06/2022":"Compliant DM 23/06/2022"} /><Row l={it?"Contenuto riciclato":"Recycled content"} v="12% post-consumer" /><Row l={it?"Riciclabilità":"Recyclability"} v={it?"100% meccanico":"100% mechanical"} /><Row l={it?"Carbon footprint (A1-A3)":"Carbon footprint (A1-A3)"} v="3.4 kg CO₂ eq/m²" /></>);
          const certs = [...(pp?.compliance?.product_certifications || []), ...(pp?.compliance?.company_certifications || [])];
          if (!certs.length) return <Row l={it?"Certificazioni":"Certifications"} v={it?"Nessuna estratta":"None extracted"} />;
          return certs.map((c, i) => { const nm = _ev(c, "name"); const ref = _ev(c, "reference_number"); return <Row key={i} l={nm || (it?"Certificazione":"Certification")} v={ref || (it?"presente":"present")} />; });
        })()}</Card>
      </div>
    </>);
    case "lifecycle": return (<LifecycleTab L={L} dppData={product} />);
    case "documenti": {
      // Real uploaded source files (from the DB), else passport's processed filenames, else demo.
      const realDocs = (product?.documents && product.documents.length)
        ? product.documents.map(d => ({ name: d.filename, size: d.size_bytes ? `${(d.size_bytes/1048576).toFixed(1)} MB` : "", type: d.doc_type }))
        : (hasAI ? (pp?.metadata?.source_documents || []).map(fn => ({ name: fn, size: "", type: null })) : null);
      const docList = realDocs || [
        {name:"DoP-XPS100-2026-001.pdf",size:"2.4 MB"},{name:"Scheda-Tecnica-XPS100.pdf",size:"1.8 MB"},
        {name:"EPD-XPS100-2025.pdf",size:"3.1 MB"},{name:"Certificato-CE.pdf",size:"0.5 MB"},
      ];
      return (<Card title="Documentation" iconD={ic.file}>
      {docList.length === 0 ? <div style={{ padding: "16px 18px", fontSize: 13, color: T.textSec, fontStyle: "italic" }}>{it?"Nessun documento caricato.":"No documents uploaded."}</div> : docList.map((d,i)=>(
        <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 18px", borderBottom: i<docList.length-1?`1px solid ${T.borderLight}`:"none" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.file} size={16} color={T.accentDark} /></div><div><div style={{ fontSize: 14, fontWeight: 600, color: T.textDark }}>{d.name}</div><div style={{ fontSize: 11, color: T.textSec }}>{[d.type, d.size].filter(Boolean).join(" — ") || (it?"documento sorgente":"source document")}</div></div></div>
          <div style={{ display: "flex", gap: 6 }}><Btn small style={{ padding: "5px 12px", fontSize: 11 }}><I d={ic.search} size={12} color={T.textSec} /></Btn><Btn small style={{ padding: "5px 12px", fontSize: 11 }}><I d={ic.download} size={12} color={T.textSec} /></Btn></div>
        </div>))}</Card>);
    }
    case "batch": {
      const hasSpecs = specDPPs.length > 0 || projCreated;
      const currentSpec = selectedSpec === "new"
        ? { batch: projBatch, site: projSite, ref: projRef, dims: projDims, weight: projWeight, date: it?"Oggi":"Today" }
        : specDPPs.find(x => x.id === selectedSpec);

      return (<div>
        {/* Header with quick "New Batch via upload" navigation (skips type selection) */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: T.navy, display: "flex", alignItems: "center", gap: 8 }}>
            <I d={ic.layers} size={16} color={T.accentDark||T.accent} />
            DPP Batch <Badge color={T.textSec} bg={T.bgSoft}>{specDPPs.length + (projCreated?1:0)}</Badge>
          </div>
          <Btn primary small onClick={()=>onNavigate("onboard-batch")} style={{ fontSize: 11, padding: "6px 14px" }}><I d={ic.plus} size={12} color={T.navy} /> {it?"Nuovo Batch":"New Batch"}</Btn>
        </div>
        {/* ─── SECTION 1: Current DPP Batch detail (top) ─── */}
        {hasSpecs && currentSpec && (<div style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: T.textSec, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              {it?"Informazioni DPP Batch":"Batch DPP Information"}
            </div>
            {selectedSpec === "new" && <Badge color={T.accent} bg={T.accentSoft}>{it?"Appena creato":"Just created"}</Badge>}
          </div>
          <div style={{ borderRadius: 10, border: `1px solid ${T.border}`, background: T.bg, overflow: "hidden" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
              <div style={{ padding: "14px 18px", borderBottom: `1px solid ${T.borderLight}`, borderRight: `1px solid ${T.borderLight}` }}><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 3 }}>{it?"Lotto":"Batch"}</div><div style={{ fontSize: 14, fontWeight: 700, color: T.navy }}>{currentSpec.batch}</div></div>
              <div style={{ padding: "14px 18px", borderBottom: `1px solid ${T.borderLight}` }}><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 3 }}>{it?"Stabilimento":"Site"}</div><div style={{ fontSize: 14, fontWeight: 700, color: T.navy }}>{currentSpec.site}</div></div>
              {currentSpec.ref && <div style={{ padding: "14px 18px", borderBottom: `1px solid ${T.borderLight}`, borderRight: `1px solid ${T.borderLight}` }}><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 3 }}>{it?"Commessa":"Order"}</div><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{currentSpec.ref}</div></div>}
              <div style={{ padding: "14px 18px", borderBottom: currentSpec.dims ? `1px solid ${T.borderLight}` : "none" }}><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 3 }}>{it?"Data":"Date"}</div><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{currentSpec.date}</div></div>
              {currentSpec.dims && <div style={{ padding: "14px 18px", borderRight: `1px solid ${T.borderLight}` }}><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 3 }}>{it?"Dimensioni":"Dimensions"}</div><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{currentSpec.dims}</div></div>}
              {currentSpec.weight && <div style={{ padding: "14px 18px" }}><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 3 }}>{it?"Peso":"Weight"}</div><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{currentSpec.weight}</div></div>}
            </div>
          </div>
        </div>)}

        {/* Empty state - no DPP Batch and none selected */}
        {!hasSpecs && (<div style={{ textAlign: "center", padding: "32px 20px", borderRadius: 10, border: `1px solid ${T.border}`, background: T.bg, marginBottom: 20 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 12px" }}><I d={ic.layers} size={22} color={T.accentDark||T.accent} /></div>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: T.navy, margin: "0 0 4px" }}>{it?"Nessun DPP Batch":"No Batch DPP"}</h3>
          <p style={{ fontSize: 12, color: T.textSec, maxWidth: 380, margin: "0 auto" }}>{it?"Crea un DPP Batch caricando un documento o compilando manualmente i campi sotto.":"Create a Batch DPP by uploading a document or filling in the fields below."}</p>
        </div>)}

        {/* ─── SECTION 2: Other DPP Batch from same Model (bottom) ─── */}
        {hasSpecs && (<div style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: T.textDark }}>{it?"Altri DPP Batch":"Other Batch DPPs"} <Badge color={T.textSec} bg={T.bgSoft}>{specDPPs.length + (projCreated ? 1 : 0)}</Badge></div>
            {(specDPPs.length + (projCreated?1:0)) >= 5 && <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 10px", borderRadius: 6, border: `1px solid ${T.border}`, width: 180 }}><I d={ic.search} size={11} color={T.textSec} /><input value={specFilter} onChange={e=>setSpecFilter(e.target.value)} placeholder={it?"Cerca...":"Search..."} style={{ flex: 1, border: "none", outline: "none", fontSize: 11, background: "transparent", fontFamily: font }} /></div>}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4, maxHeight: 200, overflowY: "auto" }}>
            {projCreated && selectedSpec !== "new" && (<div onClick={()=>setSelectedSpec("new")} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 12px", borderRadius: 7, border: `1px solid ${T.borderLight}`, background: T.bg, cursor: "pointer", transition: "border-color 0.15s" }} onMouseEnter={e=>e.currentTarget.style.borderColor=T.accent} onMouseLeave={e=>e.currentTarget.style.borderColor=T.borderLight}>
              <div style={{ width: 7, height: 7, borderRadius: "50%", background: T.accent }} />
              <div style={{ flex: 1 }}><span style={{ fontSize: 11, fontWeight: 600, color: T.textDark }}>{projBatch}</span></div>
              <Badge color={T.accent} bg={T.accentSoft} style={{ fontSize: 9 }}>{it?"Nuovo":"New"}</Badge>
            </div>)}
            {filteredSpecs.filter(s=>s.id!==selectedSpec).slice(0,5).map((s,i)=>(<div key={i} onClick={()=>setSelectedSpec(s.id)} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 12px", borderRadius: 7, border: `1px solid ${T.borderLight}`, background: T.bg, cursor: "pointer", transition: "border-color 0.15s" }} onMouseEnter={e=>e.currentTarget.style.borderColor=T.accent} onMouseLeave={e=>e.currentTarget.style.borderColor=T.borderLight}>
              <div style={{ width: 7, height: 7, borderRadius: "50%", background: s.pct===100?T.accent:T.amber }} />
              <div style={{ flex: 1 }}><span style={{ fontSize: 11, fontWeight: 600, color: T.textDark }}>{s.batch}</span> {s.ref && <span style={{ fontSize: 10, color: T.textSec }}>{s.ref}</span>}</div>
              <span style={{ fontSize: 10, color: T.textSec }}>{s.date}</span>
            </div>))}
          </div>
        </div>)}

        {/* ─── SECTION 3: Create new DPP Batch ─── */}
        <div style={{ borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", textAlign: "center" }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: T.navy, marginBottom: 4 }}>{it?"Creazione rapida Batch":"Quick Batch creation"}</div>
            <div style={{ fontSize: 11, color: T.textSec, marginBottom: 10 }}>{it?"Per AI extraction completa, usa Nuovo Batch in alto.":"For full AI extraction, use New Batch above."}</div>
            <div onClick={()=>document.getElementById("projFileInput2")?.click()} onDragOver={e=>{e.preventDefault();e.currentTarget.style.background=T.accentSoft+"60";}} onDragLeave={e=>{e.preventDefault();e.currentTarget.style.background=T.accentSoft+"20";}} onDrop={e=>{e.preventDefault();e.currentTarget.style.background=T.accentSoft+"20";const f=e.dataTransfer?.files?.[0];if(f){setProjBatch(it?"(da "+f.name+")":"(from "+f.name+")");setShowManual(true);}}} style={{ maxWidth: 360, margin: "0 auto 12px", padding: "16px 14px", borderRadius: 10, border: `2px dashed ${T.accent}`, background: T.accentSoft+"20", cursor: "pointer", transition: "all 0.15s" }} onMouseEnter={e=>e.currentTarget.style.background=T.accentSoft+"40"} onMouseLeave={e=>e.currentTarget.style.background=T.accentSoft+"20"}>
              <input id="projFileInput2" type="file" accept=".pdf,.xlsx,.xls,.csv,.docx" style={{ display: "none" }} onChange={e=>{if(e.target.files?.[0]){const f=e.target.files[0]; setProjBatch(it?"(da "+f.name+")":"(from "+f.name+")"); setShowManual(true);}}} />
              <I d={ic.upload} size={20} color={T.accent} />
              <div style={{ fontSize: 12, fontWeight: 600, color: T.accentDark||T.accent, marginTop: 4 }}>{it?"Trascina o clicca":"Drag or click"}</div>
              <div style={{ fontSize: 10, color: T.textSec, marginTop: 2 }}>PDF, Excel, Word</div>
            </div>
            <button onClick={()=>setShowManual(!showManual)} style={{ background: "none", border: "none", color: T.accent, fontSize: 11, fontWeight: 600, cursor: "pointer", fontFamily: font }}>{showManual ? (it?"Nascondi campi ▴":"Hide fields ▴") : (it?"Inserisci manualmente ▾":"Enter manually ▾")}</button>
          </div>
          {showManual && (<div style={{ padding: "0 20px 16px", borderTop: `1px solid ${T.borderLight}` }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 12, marginBottom: 8 }}>
              <div><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, marginBottom: 3 }}>{it?"Lotto *":"Batch *"}</div><input value={projBatch} onChange={e=>setProjBatch(e.target.value)} placeholder="PR-2026-047" style={{ width: "100%", padding: "6px 9px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 11, fontFamily: font, outline: "none" }} /></div>
              <div><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, marginBottom: 3 }}>{it?"Stabilimento *":"Site *"}</div><input value={projSite} onChange={e=>setProjSite(e.target.value)} placeholder={it?"Stab. Treviso":"Treviso plant"} style={{ width: "100%", padding: "6px 9px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 11, fontFamily: font, outline: "none" }} /></div>
            </div>
            <div style={{ marginBottom: 8 }}><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, marginBottom: 3 }}>{it?"Commessa":"Order"}</div><input value={projRef} onChange={e=>setProjRef(e.target.value)} placeholder={it?"Commessa Villa Marchetti":"Order Villa Marchetti"} style={{ width: "100%", padding: "6px 9px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 11, fontFamily: font, outline: "none" }} /></div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
              <div><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, marginBottom: 3 }}>{it?"Dimensioni":"Dimensions"}</div><input value={projDims} onChange={e=>setProjDims(e.target.value)} placeholder="1200×1500mm" style={{ width: "100%", padding: "6px 9px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 11, fontFamily: font, outline: "none" }} /></div>
              <div><div style={{ fontSize: 10, fontWeight: 600, color: T.textSec, marginBottom: 3 }}>{it?"Peso":"Weight"}</div><input value={projWeight} onChange={e=>setProjWeight(e.target.value)} placeholder="38 kg" style={{ width: "100%", padding: "6px 9px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 11, fontFamily: font, outline: "none" }} /></div>
            </div>
            <Btn primary onClick={()=>{
              const newId = onAddProjectDPP && onAddProjectDPP({ batch: projBatch, site: projSite, ref: projRef, dims: projDims, weight: projWeight });
              setProjCreated(true); setSelectedSpec(newId || "new"); setShowManual(false);
              setProjBatch(""); setProjSite(""); setProjRef(""); setProjDims(""); setProjWeight("");
            }} style={{ width: "100%", justifyContent: "center", fontSize: 12 }} disabled={!projBatch||!projSite}><I d={ic.plus} size={13} color={T.navy} /> {it?"Crea DPP Batch":"Create Batch DPP"}</Btn>
          </div>)}
        </div>
      </div>);
    }
    case "item": {
      // List Items belonging to selected batch (or all items when at Model level)
      const itemsToShow = currentBatch ? currentBatch.items.map(i => ({ ...i, batchLot: currentBatch.lot, batchId: currentBatch.id })) : allItems;
      const groupTitle = currentBatch
        ? (it?"Item nel Batch ":"Items in Batch ") + currentBatch.lot
        : (it?"Tutti gli Item":"All Items");
      return (<div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: T.navy, display: "flex", alignItems: "center", gap: 8 }}>
            <I d={ic.box} size={16} color="#3B82F6" />
            {groupTitle} <Badge color={T.textSec} bg={T.bgSoft}>{itemsToShow.length}</Badge>
          </div>
          <Btn primary small onClick={()=>onNavigate("onboard-item")} style={{ fontSize: 11, padding: "6px 14px" }}><I d={ic.plus} size={12} color={T.navy} /> {it?"Nuovo Item":"New Item"}</Btn>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {itemsToShow.length === 0 && (
            <div style={{ textAlign: "center", padding: "32px 20px", borderRadius: 10, border: `1px dashed ${T.border}`, background: T.bgSoft }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: (T.blueSoft||"#EFF6FF"), display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 12px" }}><I d={ic.box} size={22} color="#3B82F6" /></div>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: T.navy, margin: "0 0 4px" }}>{it?"Nessun Item":"No Items"}</h3>
              <p style={{ fontSize: 11, color: T.textSec, maxWidth: 320, margin: "0 auto 12px" }}>{it?"Crea un DPP Item per il singolo prodotto fisico.":"Create a DPP Item for individual physical products."}</p>
              <Btn primary small onClick={()=>onNavigate("onboard-item")} style={{ margin: "0 auto", fontSize: 11 }}><I d={ic.plus} size={12} color={T.navy} /> {it?"Nuovo Item":"New Item"}</Btn>
            </div>
          )}
          {itemsToShow.map((item, i) => (
            <div key={item.id} onClick={()=>{setSelectedItemId(item.id); if (item.batchId) setSelectedBatchId(item.batchId); setDppLevel("item"); setTab("panoramica");}} style={{ display: "grid", gridTemplateColumns: "auto 1fr 1fr 1fr 1fr auto", gap: 12, alignItems: "center", padding: "10px 14px", borderRadius: 8, border: `1px solid ${T.borderLight}`, background: T.bg, cursor: "pointer", transition: "border-color 0.15s" }} onMouseEnter={e=>e.currentTarget.style.borderColor="#3B82F6"} onMouseLeave={e=>e.currentTarget.style.borderColor=T.borderLight}>
              <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#3B82F6" }} />
              <div style={{ fontSize: 12, fontWeight: 700, color: T.navy }}>{item.sn}</div>
              <div style={{ fontSize: 11, color: T.textSec }}>{item.dims} · {item.weight}</div>
              <div style={{ fontSize: 11, color: T.textSec }}>{item.dest}</div>
              <div style={{ fontSize: 11, color: T.textSec }}>{!currentBatch && (<>{it?"Lotto":"Batch"}: {item.batchLot} · </>)}{item.date}</div>
              <I d={ic.chevRight} size={14} color={T.textSec} />
            </div>
          ))}
        </div>
        <div style={{ marginTop: 12, padding: "10px 14px", borderRadius: 8, background: (T.blueSoft||"#EFF6FF")+"40", border: `1px solid #3B82F630`, fontSize: 11, color: T.textSec, display: "flex", alignItems: "center", gap: 8 }}>
          <I d={ic.box} size={12} color="#3B82F6" />
          {it?"DPP Item: passaporto del singolo prodotto fisico. Ogni Item eredita dal Batch e dal Model.":"DPP Item: passport for an individual physical product. Each Item inherits from its Batch and Model."}
        </div>
      </div>);
    }
    case "versioni": return (<Card title={it?"Cronologia":"History"} iconD={ic.clock}>
      {versions.length === 0
        ? <div style={{ padding: "16px 18px", fontSize: 13, color: T.textSec, fontStyle: "italic" }}>{it?"Nessuna versione registrata. Le modifiche salvate creano una nuova versione.":"No versions yet. Saved edits create a new version."}</div>
        : versions.map((v, i) => (
          <div key={v.id || i} style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "12px 18px", borderBottom: i < versions.length - 1 ? `1px solid ${T.borderLight}` : "none" }}>
            <Badge color={T.accentDark} bg={T.accentSoft}>{v.label || `v${versions.length - i}`}</Badge>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, color: T.textDark }}>{v.change_summary || (it ? "Modifica salvata" : "Saved change")}</div>
              <div style={{ fontSize: 11, color: T.textSec }}>{v.created_at ? new Date(v.created_at).toLocaleDateString(it ? "it-IT" : "en-US", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : ""}</div>
            </div>
          </div>))}
    </Card>);
    default: return null;}};

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: font, background: T.bgSoft, overflow: "hidden" }}>
      <Sidebar activePage="passaporti" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <div style={{ flex: 1, overflowY: "auto" }}>
          <div style={{ padding: "12px 28px 0" }}><button onClick={()=>onNavigate("catalog")} style={{ background: "none", border: "none", color: T.textSec, fontSize: 12, cursor: "pointer", padding: 0, fontFamily: font, display: "flex", alignItems: "center", gap: 4 }}><I d={ic.arrow} size={12} color={T.textSec} style={{ transform: "rotate(180deg)" }} /> {_("backTo")}</button></div>
          <div style={{ padding: "16px 28px 20px", background: T.bg, borderBottom: `1px solid ${T.border}` }}>
            <div style={{ display: "flex", gap: 24 }}>
              {product?.imageUrl ? (
                <img src={product.imageUrl} alt={pname} style={{ width: 160, height: 160, borderRadius: 10, objectFit: "cover", border: `1px solid ${T.border}`, flexShrink: 0, background: T.bgSoft }} />
              ) : (
                <div style={{ width: 160, height: 160, borderRadius: 10, background: `linear-gradient(135deg, ${T.bgSoft}, ${T.accentSoft}50)`, border: `1px solid ${T.border}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <I d={ic.box} size={48} color={T.accent} style={{ opacity: 0.5 }} />
                  <div style={{ fontSize: 11, fontWeight: 600, color: T.accentDark, marginTop: 4, textAlign: "center", padding: "0 6px" }}>{familyShort}</div>
                </div>
              )}
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", gap: 6, marginBottom: 8 }}>
                  <Badge color={published?T.bg:T.amber} bg={published?T.accent:T.amberSoft}><I d={published?ic.check:ic.edit} size={9} color={published?T.navy:T.amber} /> {published?_("published"):_("preview")}</Badge>
                  {(!hasAI || rv("compliance.ce_marking", "")) && <Badge color={T.accentDark} bg={T.accentSoft}>{_("ceMark")}</Badge>}
                  <Badge color={T.textSec} bg={T.bgSoft}><I d={ic.globe} size={9} color={T.textSec} /> EU 2024/1781</Badge>
                </div>
                <h1 style={{ fontSize: 26, fontWeight: 800, color: T.navy, margin: "0 0 4px" }}>{pname}</h1>
                <div style={{ marginBottom: 8 }}><Badge color={T.textSec} bg={T.bgSoft}><I d={ic.clip} size={9} color={T.textSec} /> {puid}</Badge></div>
                <p style={{ fontSize: 13, color: T.textSec, margin: "0 0 12px", lineHeight: 1.5 }}>{rv("overview.product_info.product_description", "Pannello isolante in polistirene estruso ad alta densità per isolamento termico di pareti, pavimenti e coperture.")}</p>
                <div style={{ display: "flex", gap: 10 }}>
                  {[
                    {ic: ic.leaf, l:"CARBON", v: hasAI ? (gwpStages.length ? `${gwpTotal.toFixed(1)} kg` : (it?"n.d.":"n/a")) : "5.5 kg", s:"CO₂eq"},
                    {ic: ic.recycle, l: it?"RICICLATO":"RECYCLED", v: hasAI ? (recycledVal || (it?"n.d.":"n/a")) : "15%", s:"content"},
                    {ic: ic.recycle, l: it?"RICICLABILE":"RECYCLABLE", v: hasAI ? (it?"n.d.":"n/a") : "85%", s:"end of life"},
                    {ic: ic.energy, l: it?"ENERGIA":"ENERGY", v: hasAI ? (it?"n.d.":"n/a") : "A+", s:"class", dk:true},
                  ].map((k,i)=>(
                    <div key={i} style={{ flex: 1, padding: "10px 14px", borderRadius: 8, background: k.dk?T.navyLight:T.bgSoft, border: `1px solid ${k.dk?T.navyMid:T.border}` }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: k.dk?T.textMuted:T.textSec, textTransform: "uppercase", display: "flex", alignItems: "center", gap: 3 }}><I d={k.ic} size={10} color={k.dk?T.textMuted:T.textSec} />{k.l}</div>
                      <div style={{ fontSize: 22, fontWeight: 800, color: k.dk?T.accent:T.accentDark, marginTop: 1 }}>{k.v}</div>
                      <div style={{ fontSize: 10, color: k.dk?T.textMuted:T.textSec }}>{k.s}</div>
                    </div>))}
                </div>
                <div style={{ display: "flex", gap: 16, marginTop: 10, fontSize: 12, color: T.textSec }}>
                  <span style={{ display: "flex", alignItems: "center", gap: 3 }}><I d={ic.factory} size={12} color={T.textSec} /> {pmfr}</span>
                  {rv("overview.product_info.production_period", null) && <span style={{ display: "flex", alignItems: "center", gap: 3 }}><I d={ic.file} size={12} color={T.textSec} /> {rv("overview.product_info.production_period", "")}</span>}
                  {rv("overview.product_info.functional_unit", null) && <span style={{ display: "flex", alignItems: "center", gap: 3 }}><I d={ic.box} size={12} color={T.textSec} /> {rv("overview.product_info.functional_unit", "")}</span>}
                </div>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, flexShrink: 0, width: 170 }}>
                {!published ? (<>
                  <Btn primary onClick={() => { setPublished(true); if (onPublish && product?.id) onPublish(product.id); }} style={{ width: "100%", justifyContent: "center" }}><I d={ic.check} size={14} color={T.navy} /> {_("publish")}</Btn>
                  <button onClick={() => setShowPublicDPP(true)} style={{ background: "none", border: "none", color: T.accent, fontSize: 11, fontWeight: 600, cursor: "pointer", fontFamily: font, padding: "4px 0" }}>{it?"Anteprima DPP →":"Preview DPP →"}</button>
                </>) : (<>
                  <div style={{ padding: "8px 10px", borderRadius: 8, background: T.accentSoft, border: `1px solid ${T.accent}30`, textAlign: "center", marginBottom: 2 }}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: T.accentDark }}><I d={ic.check} size={9} color={T.accentDark} /> {_("published")}</div>
                  </div>
                  <Btn primary onClick={()=>setShowPublicDPP(true)} style={{ width: "100%", justifyContent: "center", fontSize: 12 }}><I d={ic.globe} size={14} color={T.navy} /> {it?"DPP Pubblico":"Public DPP"}</Btn>
                  {/* Export dropdown */}
                  <div style={{ position: "relative" }}>
                    <Btn onClick={()=>setShowExport(!showExport)} style={{ width: "100%", justifyContent: "center" }}><I d={ic.download} size={14} color={T.textDark} /> Export {showExport?"▴":"▾"}</Btn>
                    {showExport && <div style={{ position: "absolute", top: "100%", left: 0, right: 0, marginTop: 4, background: T.bg, border: `1px solid ${T.border}`, borderRadius: 8, boxShadow: "0 8px 24px rgba(0,0,0,0.12)", zIndex: 10, overflow: "hidden" }}>
                      {[[ic.download, it?"Scarica PDF":"Download PDF", generatePDF], [ic.share, "Export CSV", ()=>setShowCSV(true)], [ic.grid, "QR Code", ()=>setShowQR(true)], [ic.link, "Embed", ()=>setShowEmbed(true)]].map(([d,l,fn],i)=>(
                        <button key={i} onClick={()=>{fn();setShowExport(false);}} style={{ display: "flex", alignItems: "center", gap: 8, width: "100%", padding: "9px 14px", background: "none", border: "none", borderBottom: i<3?`1px solid ${T.borderLight}`:"none", cursor: "pointer", fontFamily: font, fontSize: 12, color: T.textDark, fontWeight: 500 }}><I d={d} size={13} color={T.textSec} />{l}</button>
                      ))}
                    </div>}
                  </div>
                </>)}
                <Btn onClick={()=>onNavigate("app-edit")} style={{ width: "100%", justifyContent: "center" }}><I d={ic.edit} size={14} color={T.textDark} /> {_("edit")}</Btn>
                <Btn small onClick={()=>setChatOpen(!chatOpen)} style={{ width: "100%", justifyContent: "center", border: `1px solid ${chatOpen?T.accent:T.border}`, background: chatOpen?T.accentSoft:T.bg, color: chatOpen?T.accentDark:T.textSec }}><I d={ic.msg} size={13} color={chatOpen?T.accentDark:T.textSec} /> {_("assistant")}</Btn>
              </div>
            </div>
          </div>
          {/* ─── DPP Level switcher (Model / Batch / Item) ─── */}
          <div style={{ padding: "10px 28px", background: T.bg, borderBottom: `1px solid ${T.borderLight}`, display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <span style={{ fontSize: 10, fontWeight: 700, color: T.textSec, textTransform: "uppercase", letterSpacing: "0.06em" }}>{it?"Livello DPP":"DPP Level"}</span>
            <div style={{ display: "flex", gap: 4, padding: 3, borderRadius: 7, background: T.bgSoft, border: `1px solid ${T.borderLight}` }}>
              {[
                ["model", "Model", T.navy, T.bgSoft, ic.box],
                ["batch", "Batch", T.accentDark||T.accent, T.accentSoft, ic.layers],
                ["item", "Item", "#3B82F6", T.blueSoft||"#EFF6FF", ic.box],
              ].map(([lvl, lbl, color, bg, iconD]) => {
                const active = dppLevel === lvl;
                const hasBatches = perenneData.batches.length > 0;
                const hasItems = allItems.length > 0;
                const enabled =
                  lvl === "model"
                  || (lvl === "batch" && hasBatches)
                  || (lvl === "item" && (hasItems || dppLevel === "item"));
                return (
                  <button key={lvl} onClick={() => {
                    if (!enabled || active) return;
                    setDppLevel(lvl);
                    if (lvl === "model") { setSelectedBatchId(null); setSelectedItemId(null); }
                    if (lvl === "batch" && !selectedBatchId && hasBatches) { setSelectedBatchId(perenneData.batches[0].id); }
                    if (lvl === "item" && !selectedItemId && hasItems) { setSelectedItemId(allItems[0].id); setSelectedBatchId(allItems[0].batchId); }
                    // After level change, reset tab to a valid one
                    setTab("panoramica");
                  }} disabled={!enabled} style={{ padding: "5px 12px", borderRadius: 5, border: "none", background: active ? color : "transparent", color: active ? "#fff" : enabled ? T.textDark : T.textSec, fontSize: 11, fontWeight: 600, cursor: enabled ? "pointer" : "not-allowed", fontFamily: font, display: "flex", alignItems: "center", gap: 5, opacity: enabled ? 1 : 0.5, transition: "all 0.15s" }}>
                    <I d={iconD} size={11} color={active ? "#fff" : enabled ? color : T.textSec} />
                    {lbl}
                  </button>
                );
              })}
            </div>
            {/* Back-up navigation: Back to Model (always when not on Model) / Back to Batch (when on Item from a batch) */}
            {dppLevel !== "model" && (
              <button onClick={() => { setDppLevel("model"); setSelectedBatchId(null); setSelectedItemId(null); setTab("panoramica"); }} style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px", borderRadius: 6, border: `1px solid ${T.border}`, background: T.bg, fontSize: 11, fontWeight: 600, color: T.textDark, cursor: "pointer", fontFamily: font }}>
                <I d={ic.chevLeft || ic.arrow} size={11} color={T.textSec} />
                {it?"Torna al Model":"Back to Model"}
              </button>
            )}
            {dppLevel === "item" && selectedBatchId && currentBatch && (
              <button onClick={() => { setDppLevel("batch"); setSelectedItemId(null); setTab("item"); }} style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px", borderRadius: 6, border: `1px solid ${T.accent}30`, background: T.accentSoft+"40", fontSize: 11, fontWeight: 600, color: T.accentDark||T.accent, cursor: "pointer", fontFamily: font }}>
                <I d={ic.chevLeft || ic.arrow} size={11} color={T.accentDark||T.accent} />
                {it?"Torna al Batch ":"Back to Batch "}{currentBatch.lot}
              </button>
            )}
            {dppLevel === "batch" && currentBatch && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 10px", borderRadius: 6, background: T.accentSoft, fontSize: 11, fontWeight: 600, color: T.accentDark||T.accent }}>
                <I d={ic.layers} size={11} color={T.accentDark||T.accent} />
                {currentBatch.lot} <span style={{ color: T.textSec, fontWeight: 400 }}>· {currentBatch.site}</span>
                <button onClick={() => { setSelectedBatchId(null); setDppLevel("model"); setTab("panoramica"); }} style={{ background: "none", border: "none", cursor: "pointer", color: T.textSec, padding: 0, marginLeft: 4 }}><I d={ic.x} size={10} color={T.textSec} /></button>
              </div>
            )}
            {dppLevel === "item" && currentItem && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 10px", borderRadius: 6, background: (T.blueSoft||"#EFF6FF"), fontSize: 11, fontWeight: 600, color: "#3B82F6" }}>
                <I d={ic.box} size={11} color="#3B82F6" />
                {currentItem.sn} <span style={{ color: T.textSec, fontWeight: 400 }}>· {currentItem.dims} · {currentItem.dest}</span>
                <button onClick={() => { setSelectedItemId(null); setDppLevel(selectedBatchId ? "batch" : "model"); setTab("panoramica"); }} style={{ background: "none", border: "none", cursor: "pointer", color: T.textSec, padding: 0, marginLeft: 4 }}><I d={ic.x} size={10} color={T.textSec} /></button>
              </div>
            )}
            <div style={{ flex: 1 }} />
            <Badge color={dppLevel==="model"?T.textSec:dppLevel==="batch"?(T.accentDark||T.accent):"#3B82F6"} bg={dppLevel==="model"?T.bgSoft:dppLevel==="batch"?T.accentSoft:(T.blueSoft||"#EFF6FF")}>DPP {levelLabel}</Badge>
          </div>
          <div style={{ padding: "0 28px", background: T.bg, borderBottom: `1px solid ${T.border}` }}>
            <div style={{ display: "flex", gap: 0, flexWrap: "wrap", alignItems: "flex-end" }}>
              <div style={{ display: "flex", gap: 0 }}>
                {prodTabs.map(t=>(<button key={t.key} onClick={()=>setTab(t.key)} style={{ padding: "9px 14px", border: "none", borderBottom: `2px solid ${tab===t.key?T.accent:"transparent"}`, background: "transparent", fontSize: 12, fontWeight: tab===t.key?700:500, color: tab===t.key?T.textDark:T.textSec, cursor: "pointer", fontFamily: font, display: "flex", alignItems: "center", gap: 5, marginBottom: -1 }}><I d={t.d} size={12} color={tab===t.key?T.accentDark:T.textSec} />{t.label}</button>))}
              </div>
              <div style={{ width: 1, height: 20, background: T.border, margin: "0 6px 6px", flexShrink: 0 }} />
              <div style={{ display: "flex", gap: 0 }}>
                {mgmtTabs.map(t=>(<button key={t.key} onClick={()=>setTab(t.key)} style={{ padding: "9px 14px", border: "none", borderBottom: `2px solid ${tab===t.key?T.accent:"transparent"}`, background: "transparent", fontSize: 12, fontWeight: tab===t.key?700:500, color: tab===t.key?T.textDark:T.textSec, cursor: "pointer", fontFamily: font, display: "flex", alignItems: "center", gap: 5, marginBottom: -1 }}><I d={t.d} size={12} color={tab===t.key?T.accentDark:T.textSec} />{t.label}</button>))}
              </div>
            </div>
          </div>
          <div style={{ padding: "20px 28px 40px" }}>{renderTab()}</div>
        </div>
        <ChatPanel open={chatOpen} onClose={()=>setChatOpen(false)} L={L} productId={product?.id} />
      </div>
      {showEmbed && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(15,23,41,0.6)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: 20 }} onClick={() => setShowEmbed(false)}>
          <div onClick={e => e.stopPropagation()} style={{ width: "100%", maxWidth: 720, maxHeight: "90vh", overflowY: "auto", background: T.bgSoft, borderRadius: 16, boxShadow: "0 24px 48px rgba(0,0,0,0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 24px", borderBottom: `1px solid ${T.border}` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><Logo dark size={18} /><Badge color={T.accentDark} bg={T.accentSoft}>EMBED PREVIEW</Badge></div>
              <button onClick={() => setShowEmbed(false)} style={{ background: "none", border: "none", cursor: "pointer", padding: 4 }}><I d={ic.x} size={18} color={T.textSec} /></button>
            </div>
            <div style={{ margin: "20px 24px", background: T.bg, borderRadius: 12, border: `1px solid ${T.border}`, overflow: "hidden" }}>
              <div style={{ display: "flex", gap: 14, padding: "18px 20px", borderBottom: `1px solid ${T.borderLight}` }}>
                <div style={{ width: 72, height: 72, borderRadius: 8, background: `linear-gradient(135deg, ${T.bgSoft}, ${T.accentSoft}50)`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, border: `1px solid ${T.borderLight}` }}><I d={ic.box} size={28} color={T.accent} style={{ opacity: 0.5 }} /></div>
                <div>
                  <div style={{ fontSize: 17, fontWeight: 800, color: T.navy, marginBottom: 3 }}>{pname}</div>
                  <div style={{ fontSize: 12, color: T.textSec, marginBottom: 6 }}>{`${pmfr} — ${puid}`}</div>
                  <div style={{ display: "flex", gap: 4 }}><Badge color={T.accentDark} bg={T.accentSoft}>CE</Badge><Badge color={T.accentDark} bg={T.accentSoft}>EPD</Badge><Badge color={T.accentDark} bg={T.accentSoft}>ESPR 2024/1781</Badge></div>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", borderBottom: `1px solid ${T.borderLight}` }}>
                {[["GWP","5.5","kgCO₂eq/m²"],[it?"Riciclato":"Recycled","15%",it?"contenuto":"content"],[it?"Riciclabile":"Recyclable","85%",it?"fine vita":"end of life"],[it?"Energia":"Energy","A+",it?"classe":"class"]].map(([l,v,u],i)=>(
                  <div key={i} style={{ padding: "12px 14px", textAlign: "center", borderRight: i<3?`1px solid ${T.borderLight}`:"none" }}>
                    <div style={{ fontSize: 9, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: T.textSec }}>{l}</div>
                    <div style={{ fontSize: 20, fontWeight: 800, color: T.accentDark, marginTop: 2 }}>{v}</div>
                    <div style={{ fontSize: 9, color: T.textSec }}>{u}</div>
                  </div>
                ))}
              </div>
              <div style={{ padding: "8px 20px 4px", background: T.bgSoft, fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: T.accentDark }}>{it?"Prestazioni chiave":"Key Performance"}</div>
              {[[it?"Conducibilità termica (λ)":"Thermal Conductivity (λ)","0.034 W/(m·K)"],[it?"Resistenza a compressione":"Compressive Strength","300 kPa"],[it?"Classe reazione al fuoco":"Fire Reaction Class","E (EN 13501-1)"],[it?"Assorbimento acqua":"Water Absorption","≤ 0.7% vol"]].map(([l,v],i)=>(
                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 20px", borderBottom: `1px solid ${T.borderLight}`, fontSize: 12 }}><span style={{ color: T.textSec }}>{l}</span><span style={{ fontWeight: 600, color: T.textDark }}>{v}</span></div>
              ))}
              <div style={{ padding: "8px 20px 4px", background: T.bgSoft, fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: T.accentDark }}>{it?"Conformità":"Compliance"}</div>
              {[[it?"Marcatura CE":"CE Marking",(it?"Conforme":"Compliant")+" — 0123-CPR-2024"],["Standard","EN 13164:2012+A1:2015"],["SVHC / CMR / PFAS","No / No / No"]].map(([l,v],i)=>(
                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "6px 20px", borderBottom: `1px solid ${T.borderLight}`, fontSize: 12 }}><span style={{ color: T.textSec }}>{l}</span><span style={{ fontWeight: 600, color: T.textDark }}>{v}</span></div>
              ))}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 20px", background: T.bgSoft, fontSize: 10, color: T.textSec }}>
                <span style={{ color: T.accentDark, fontWeight: 600 }}>{it?"Visualizza DPP completo su DeePPy →":"View full DPP on DeePPy →"}</span>
                <span>{it?"Aggiornato automaticamente":"Auto-updated"} · v1.2</span>
              </div>
            </div>
            <div style={{ margin: "0 24px 20px", background: T.navy, borderRadius: 10, padding: "16px 20px" }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: T.text, marginBottom: 8 }}>{it?"Codice embed per il tuo sito":"Embed code for your website"}</div>
              <div style={{ background: T.navyLight, borderRadius: 6, padding: "12px 14px", fontSize: 11, color: T.accent, fontFamily: "'Courier New', monospace", lineHeight: 1.6, wordBreak: "break-all" }}>
                {`<iframe src="https://deeppy.eu/embed/${puid}"`}<br/>
                {'  width="100%" height="720" frameborder="0"'}<br/>
                {'  style="border:1px solid #E2E8F0;border-radius:12px;max-width:800px">'}<br/>
                {'</iframe>'}
              </div>
              <div style={{ fontSize: 11, color: T.textMuted, marginTop: 8 }}>{it?"Il widget si aggiorna automaticamente quando aggiorni il DPP su DeePPy.":"The widget updates automatically when you update the DPP on DeePPy."}</div>
              <Btn small primary onClick={() => { try { navigator.clipboard.writeText(`<iframe src="https://deeppy.eu/embed/${puid}" width="100%" height="720" frameborder="0" style="border:1px solid #E2E8F0;border-radius:12px;max-width:800px"></iframe>`); const el=document.getElementById("embed-copied"); if(el){el.style.opacity="1";setTimeout(()=>el.style.opacity="0",1500);} } catch(e) {} }} style={{ marginTop: 10, width: "100%" }}><I d={ic.check} size={13} color={T.navy} /> {it?"Copia codice embed":"Copy embed code"}</Btn><div id="embed-copied" style={{ textAlign: "center", fontSize: 11, fontWeight: 600, color: T.accent, marginTop: 6, opacity: 0, transition: "opacity 0.3s" }}>{it?"Copiato!":"Copied!"}</div>
            </div>
          </div>
        </div>
      )}
      {/* CSV Modal */}
      {showCSV && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(15,23,41,0.6)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: 20 }} onClick={() => setShowCSV(false)}>
          <div onClick={e => e.stopPropagation()} style={{ width: "100%", maxWidth: 680, maxHeight: "90vh", overflowY: "auto", background: T.bgSoft, borderRadius: 16, boxShadow: "0 24px 48px rgba(0,0,0,0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 24px", borderBottom: `1px solid ${T.border}` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><Logo dark size={18} /><Badge color={T.accentDark} bg={T.accentSoft}>EXPORT CSV</Badge></div>
              <button onClick={() => setShowCSV(false)} style={{ background: "none", border: "none", cursor: "pointer", padding: 4 }}><I d={ic.x} size={18} color={T.textSec} /></button>
            </div>
            <div style={{ padding: "16px 24px" }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: T.textDark, marginBottom: 4 }}>{pname}</div>
              <div style={{ fontSize: 12, color: T.textSec, marginBottom: 16 }}>{csvData.length - 1} {it?"campi":"fields"} · {puid} · {csvData[0].length} {it?"colonne":"columns"}</div>
              <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden", maxHeight: 340, overflowY: "auto", overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 10, minWidth: 600 }}>
                  <thead><tr style={{ background: T.navy }}>
                    {csvData[0].map((h,i) => <th key={i} style={{ padding: "6px 8px", textAlign: "left", color: T.text, fontWeight: 700, fontSize: 9, textTransform: "uppercase", letterSpacing: "0.04em", whiteSpace: "nowrap" }}>{h}</th>)}
                  </tr></thead>
                  <tbody>{csvData.slice(1).map((r,i) => (
                    <tr key={i} style={{ borderBottom: `1px solid ${T.borderLight}`, background: i%2===0?T.bg:T.bgSoft }}>
                      {r.map((c,j) => <td key={j} style={{ padding: "4px 8px", color: j===0?T.accentDark:j===r.length-1?T.textDark:T.textSec, fontWeight: j===r.length-1?600:400, maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c}</td>)}
                    </tr>
                  ))}</tbody>
                </table>
              </div>
              <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
                <Btn small primary onClick={() => { downloadCSV(); setShowCSV(false); }} style={{ flex: 1 }}><I d={ic.download} size={13} color={T.navy} /> {it?"Scarica CSV":"Download CSV"}</Btn>
                <Btn small onClick={() => setShowCSV(false)} style={{ flex: 1 }}>{it?"Chiudi":"Close"}</Btn>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* QR Code Modal */}
      {showQR && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(15,23,41,0.6)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: 20 }} onClick={() => setShowQR(false)}>
          <div onClick={e => e.stopPropagation()} style={{ width: "100%", maxWidth: 420, background: T.bg, borderRadius: 16, boxShadow: "0 24px 48px rgba(0,0,0,0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 24px", borderBottom: `1px solid ${T.border}` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}><Logo dark size={18} /><Badge color={T.accentDark} bg={T.accentSoft}>QR CODE</Badge></div>
              <button onClick={() => setShowQR(false)} style={{ background: "none", border: "none", cursor: "pointer", padding: 4 }}><I d={ic.x} size={18} color={T.textSec} /></button>
            </div>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "28px 24px" }}>
              <svg data-qr="1" viewBox="0 0 210 210" style={{ width: 200, height: 200, marginBottom: 16 }}>
                <rect width="210" height="210" fill="white" rx="8" />
                {/* QR finder patterns (3 corners) */}
                <rect x="12" y="12" width="56" height="56" rx="6" fill={T.navy} />
                <rect x="20" y="20" width="40" height="40" rx="3" fill="white" />
                <rect x="28" y="28" width="24" height="24" rx="2" fill={T.navy} />
                <rect x="142" y="12" width="56" height="56" rx="6" fill={T.navy} />
                <rect x="150" y="20" width="40" height="40" rx="3" fill="white" />
                <rect x="158" y="28" width="24" height="24" rx="2" fill={T.navy} />
                <rect x="12" y="142" width="56" height="56" rx="6" fill={T.navy} />
                <rect x="20" y="150" width="40" height="40" rx="3" fill="white" />
                <rect x="28" y="158" width="24" height="24" rx="2" fill={T.navy} />
                {/* Data modules - branded pattern */}
                {[
                  [80,12],[92,12],[104,12],[116,12],[128,12],
                  [80,24],[104,24],[128,24],
                  [80,36],[92,36],[104,36],[116,36],[128,36],
                  [12,80],[24,80],[36,80],[48,80],[56,80],[80,80],[92,80],[116,80],[128,80],[142,80],[154,80],[166,80],[178,80],[186,80],
                  [12,92],[36,92],[56,92],[80,92],[104,92],[128,92],[142,92],[166,92],[186,92],
                  [12,104],[24,104],[36,104],[48,104],[56,104],[80,104],[92,104],[116,104],[128,104],[142,104],[154,104],[166,104],[178,104],[186,104],
                  [80,116],[92,116],[104,116],[116,116],[128,116],
                  [80,128],[116,128],
                  [80,140],[92,140],[104,140],[116,140],[128,140],
                  [142,142],[154,142],[166,142],[178,142],[186,142],
                  [142,154],[186,154],
                  [142,166],[154,166],[166,166],[178,166],[186,166],
                  [142,178],[166,178],
                  [142,186],[154,186],[166,186],[178,186],[186,186],
                ].map(([x,y],i) => <rect key={i} x={x} y={y} width="10" height="10" rx="1" fill={i%7===0?T.accent:T.navy} />)}
                {/* DeePPy logo center */}
                <rect x="86" y="86" width="38" height="38" rx="6" fill="white" stroke={T.border} strokeWidth="1" />
                <text x="105" y="108" textAnchor="middle" fontSize="10" fontWeight="800" fontFamily="Inter, sans-serif" fill={T.navy}>D<tspan fill={T.accent}>PP</tspan></text>
              </svg>
              <div style={{ fontSize: 16, fontWeight: 800, color: T.navy, marginBottom: 2 }}>{pname}</div>
              <div style={{ fontSize: 12, color: T.textSec, marginBottom: 4 }}>{puid}</div>
              <div style={{ fontSize: 11, color: T.textSec, marginBottom: 16 }}>{`deeppy.eu/dpp/${puid}`}</div>
              <div style={{ display: "flex", gap: 8, width: "100%" }}>
                <Btn small primary onClick={() => {
                  const svgEl = document.querySelector("[data-qr]");
                  if (!svgEl) return;
                  const svgStr = new XMLSerializer().serializeToString(svgEl);
                  const b = new Blob([svgStr], {type:"image/svg+xml"});
                  const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = "DPP-XPS100-QR.svg"; document.body.appendChild(a); a.click(); document.body.removeChild(a);
                }} style={{ flex: 1 }}><I d={ic.download} size={13} color={T.navy} /> {it?"Scarica SVG":"Download SVG"}</Btn>
                <Btn small onClick={() => setShowQR(false)} style={{ flex: 1 }}>{it?"Chiudi":"Close"}</Btn>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* DPP Public Overlay */}
      {showPublicDPP && (
        <div style={{ position: "fixed", inset: 0, zIndex: 1000, display: "flex", justifyContent: "center", alignItems: "stretch" }}>
          <div onClick={() => setShowPublicDPP(false)} style={{ position: "absolute", inset: 0, background: "rgba(15,23,41,0.6)", backdropFilter: "blur(4px)" }} />
          <div style={{ position: "relative", width: "100%", maxWidth: "min(780px, 92vw)", margin: "20px 0", background: T.bg, borderRadius: 16, overflow: "hidden", display: "flex", flexDirection: "column", boxShadow: "0 25px 60px rgba(0,0,0,0.3)", zIndex: 1001 }}>
            <button onClick={() => setShowPublicDPP(false)} style={{ position: "absolute", top: 12, right: 12, zIndex: 10, width: 32, height: 32, borderRadius: 8, background: "rgba(15,23,41,0.7)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.x} size={16} color="#F1F5F9" /></button>
            <div style={{ flex: 1, overflowY: "auto" }}>
              <PublicDPPView L={L} dppData={product?.dppData} imageUrl={product?.imageUrl} />
            </div>
          </div>
        </div>
      )}
    </div>);
}


// ─── DASHBOARD ────────────────────────────────────────────
function DashboardView({ onNavigate, L, products = [], onSelectProduct, onDelete }) {
  const it = L?.lang === "it";
  const [expandedProd, setExpandedProd] = useState(null);
  const [specSearch, setSpecSearch] = useState("");

  // Map real products to dashboard cards, with demo fallback when empty
  const demoProds = [
    { id: "demo-1", name: "Biomattone HC200", mfr: "Verdecalce Srl", pct: 82, status: "published", date: "18 Feb 2026", catIcon: "box", prodType: "industrial", specifics: [
      { id: "sp-bio-1", ref: "Lotto PR-2026-047", site: it?"Stab. Porcari":"Porcari plant", date: "15 Mar 2026", pct: 95 },
      { id: "sp-bio-2", ref: "Lotto PR-2026-046", site: it?"Stab. Porcari":"Porcari plant", date: "1 Mar 2026", pct: 100 },
      { id: "sp-bio-3", ref: "Lotto PR-2026-038", site: it?"Stab. Porcari":"Porcari plant", date: "15 Feb 2026", pct: 100 },
    ]},
    { id: "demo-2", name: "Malta Premiscelata M15", mfr: "Grigia Cementi SpA", pct: 91, status: "published", date: "12 Feb 2026", catIcon: "layers", prodType: "industrial", specifics: [] },
    { id: "demo-3", name: "Serramento Legno-Alluminio 3G", mfr: "Euroserramenti Srl", pct: 68, status: "draft", date: "20 Feb 2026", catIcon: "window", prodType: "bespoke", specifics: [
      { id: "sp-serr-1", ref: it?"Comm. Villa Marchetti":"Order Villa Marchetti", site: it?"Stab. Treviso":"Treviso plant", date: "18 Mar 2026", pct: 72, custom: "1200\u00d71500mm, 38kg" },
    ]},
  ];

  const realProds = products.map(p => ({
    id: p.id,
    name: p.name || "Unnamed Product",
    mfr: p.manufacturer || "",
    pct: p.completeness || 0,
    status: p.status || "draft",
    date: new Date(p.createdAt).toLocaleDateString(it ? "it-IT" : "en-US", { day: "numeric", month: "short", year: "numeric" }),
    catIcon: "box",
    prodType: "industrial",
    specifics: (p.projectDPPs || []).map(proj => ({
      id: proj.id,
      ref: [proj.batch, proj.ref].filter(Boolean).join(" \u2014 "),
      site: proj.site || "",
      date: proj.createdAt ? new Date(proj.createdAt).toLocaleDateString(it ? "it-IT" : "en-US", { day: "numeric", month: "short", year: "numeric" }) : "",
      pct: 100,
      custom: [proj.dims, proj.weight].filter(Boolean).join(", "),
    })),
  }));

  const prods = realProds.length > 0 ? realProds : demoProds;
  // Batch count = sum of specifics for industrial products; Item count = bespoke product specifics
  const totalBatches = prods.filter(p => p.prodType !== "bespoke").reduce((a, p) => a + p.specifics.length, 0);
  const totalItems = prods.filter(p => p.prodType === "bespoke").reduce((a, p) => a + p.specifics.length, 0);
  const publishedCount = prods.filter(p => p.status === "published").length;
  const avgPct = prods.length > 0 ? Math.round(prods.reduce((a, p) => a + p.pct, 0) / prods.length) : 0;
  const stats = [
    { label: it ? "DPP Model" : "DPP Models", value: String(prods.length), ic: ic.grid },
    { label: it ? "DPP Batch" : "Batches", value: String(totalBatches), ic: ic.layers },
    { label: it ? "DPP Item" : "Items", value: String(totalItems), ic: ic.box },
    { label: it ? "Pubblicati" : "Published", value: String(publishedCount), ic: ic.check },
    { label: it ? "Completezza media" : "Avg. completeness", value: avgPct + "%", ic: ic.chart },
  ];
  return (
    <div style={{ fontFamily: font, minHeight: "100vh", display: "flex" }}>
      <Sidebar activePage="dashboard" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, padding: "32px 40px", overflowY: "auto", background: T.bgSoft }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <div><h1 style={{ fontSize: 24, fontWeight: 800, color: T.navy, marginBottom: 2 }}>Dashboard</h1><p style={{ fontSize: 13, color: T.textSec }}>{it ? "I tuoi passaporti digitali" : "Your digital passports"}</p></div>
          <Btn primary onClick={() => onNavigate("onboard")} small style={{ fontSize: 12, padding: "8px 18px" }}><I d={ic.plus} size={13} color={T.navy} /> {it ? "Nuovo passaporto" : "New passport"}</Btn>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12, marginBottom: 28 }}>
          {stats.map((s, i) => (<div key={i} style={{ padding: "14px 16px", borderRadius: 10, background: T.bg, border: `1px solid ${T.border}` }}><div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}><I d={s.ic} size={14} color={T.accent} /><span style={{ fontSize: 10, color: T.textSec, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em" }}>{s.label}</span></div><div style={{ fontSize: 26, fontWeight: 800, color: T.navy }}>{s.value}</div></div>))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
          {prods.map((p, i) => {
            const isExp = expandedProd === i;
            const filtered = p.specifics.filter(s => !specSearch || s.ref.toLowerCase().includes(specSearch.toLowerCase()));
            const isReal = !p.id.startsWith("demo-");
            const doDelete = (e) => {
              e.stopPropagation();
              if (!onDelete || !isReal) return;
              const msg = it ? `Eliminare definitivamente "${p.name}"? L'azione non è reversibile.` : `Permanently delete "${p.name}"? This cannot be undone.`;
              if (window.confirm(msg)) onDelete(p.id);
            };
            return (<div key={i} style={{ position: "relative", borderRadius: 12, background: T.bg, border: `1px solid ${isExp ? T.accent+"50" : T.border}`, fontFamily: font, textAlign: "left", transition: "border-color 0.15s" }}>
              {isReal && onDelete && (
                <button onClick={doDelete} title={it?"Elimina passaporto":"Delete passport"} style={{ position: "absolute", top: 12, right: 12, width: 26, height: 26, borderRadius: 6, background: T.bg, border: `1px solid ${T.borderLight}`, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2, color: T.textSec, fontFamily: font }} onMouseEnter={e=>{e.currentTarget.style.color=T.red; e.currentTarget.style.borderColor=T.red+"60";}} onMouseLeave={e=>{e.currentTarget.style.color=T.textSec; e.currentTarget.style.borderColor=T.borderLight;}}>
                  <I d={ic.trash || ic.x} size={13} color="currentColor" />
                </button>
              )}
              <button onClick={() => { if (onSelectProduct && isReal) onSelectProduct(p.id, p.status === "published" ? "app" : "app-edit"); else onNavigate(p.status === "published" ? "app" : "app-edit"); }} style={{ padding: "20px 20px 12px", width: "100%", background: "none", border: "none", cursor: "pointer", fontFamily: font, textAlign: "left" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}><div style={{ width: 40, height: 40, borderRadius: 10, background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic[p.catIcon] || ic.box} size={18} color={T.accent} /></div><div style={{ flex: 1 }}><div style={{ fontSize: 14, fontWeight: 700, color: T.navy }}>{p.name}</div><div style={{ fontSize: 11, color: T.textSec }}>{p.mfr}</div></div></div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}><div style={{ flex: 1, height: 6, borderRadius: 3, background: T.borderLight, overflow: "hidden" }}><div style={{ width: `${p.pct}%`, height: "100%", borderRadius: 3, background: p.pct >= 85 ? T.accent : p.pct >= 70 ? T.amber : T.red }} /></div><span style={{ fontSize: 13, fontWeight: 700, color: T.navy }}>{p.pct}%</span></div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><Badge color={p.status === "published" ? T.accent : T.amber} bg={p.status === "published" ? T.accentSoft : T.amberSoft}>{p.status === "published" ? (it ? "Pubblicato" : "Published") : (it ? "Bozza" : "Draft")}</Badge><span style={{ fontSize: 10, color: T.textSec }}>{p.date}</span></div>
              </button>
              {/* Expand toggle for specifics */}
              <button onClick={(e) => { e.stopPropagation(); setExpandedProd(isExp ? null : i); setSpecSearch(""); }} style={{ width: "100%", padding: "10px 20px", background: isExp ? T.accentSoft+"30" : "none", border: "none", borderTop: `1px solid ${T.borderLight}`, cursor: "pointer", fontFamily: font, display: "flex", alignItems: "center", justifyContent: "space-between", transition: "background 0.15s" }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: p.specifics.length > 0 ? T.navy : T.textSec, display: "flex", alignItems: "center", gap: 6 }}><I d={ic.clip} size={12} color={p.specifics.length > 0 ? T.accent : T.textSec} />{p.specifics.length} {p.prodType==="bespoke" ? "Batch/Item" : "Batch"}</span>
                <I d={isExp ? ic.chevDown : ic.chevRight} size={14} color={T.textSec} />
              </button>
              {isExp && (<div style={{ padding: "10px 14px 14px", borderTop: `1px solid ${T.borderLight}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
                  <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 6, padding: "7px 10px", borderRadius: 7, border: `1px solid ${T.border}`, background: T.bg }}>
                    <I d={ic.search} size={12} color={T.textSec} />
                    <input value={specSearch} onChange={e => setSpecSearch(e.target.value)} placeholder={it?"Cerca lotto, commessa...":"Search batch, order..."} style={{ flex: 1, border: "none", outline: "none", fontSize: 11, background: "transparent", fontFamily: font }} />
                  </div>
                  <Badge color={T.textSec} bg={T.bgSoft}>{p.specifics.length}</Badge>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                  {filtered.slice(0, 5).map((s, si) => (<div key={si} onClick={() => onNavigate("app")} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", borderRadius: 8, border: `1px solid ${T.borderLight}`, background: T.bg, cursor: "pointer", transition: "border-color 0.15s" }} onMouseEnter={e=>e.currentTarget.style.borderColor=T.accent} onMouseLeave={e=>e.currentTarget.style.borderColor=T.borderLight}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.pct === 100 ? T.accent : T.amber, flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: T.textDark, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{s.ref}</div>
                      <div style={{ fontSize: 10, color: T.textSec, marginTop: 1 }}>{s.site} {s.custom ? `\u00b7 ${s.custom}` : ""}</div>
                    </div>
                    <div style={{ textAlign: "right", flexShrink: 0 }}>
                      <div style={{ fontSize: 10, color: T.textSec }}>{s.date}</div>
                      <div style={{ fontSize: 10, fontWeight: 600, color: s.pct === 100 ? T.accent : T.amber }}>{s.pct}%</div>
                    </div>
                  </div>))}
                  {filtered.length > 5 && <div style={{ fontSize: 11, color: T.accent, textAlign: "center", padding: 6, fontWeight: 600, cursor: "pointer" }}>{it?"Mostra tutti":"Show all"} ({filtered.length})</div>}
                  {filtered.length === 0 && <div style={{ fontSize: 11, color: T.textSec, textAlign: "center", padding: 10 }}>{it?"Nessun risultato":"No results"}</div>}
                </div>
                <button onClick={() => onNavigate(p.prodType==="bespoke" ? "onboard-item" : "onboard-batch")} style={{ width: "100%", marginTop: 10, padding: "9px 0", borderRadius: 7, border: `1px dashed ${T.accent}`, background: T.accentSoft+"30", cursor: "pointer", fontFamily: font, fontSize: 12, fontWeight: 600, color: T.accentDark||T.accent, display: "flex", alignItems: "center", justifyContent: "center", gap: 5 }}><I d={ic.plus} size={12} color={T.accentDark||T.accent} /> {p.prodType==="bespoke"?(it?"Nuovo Item":"New Item"):(it?"Nuovo Batch":"New Batch")}</button>
              </div>)}
            </div>);
          })}
          <button onClick={() => onNavigate("onboard")} style={{ padding: "20px", borderRadius: 12, background: T.bg, border: `2px dashed ${T.border}`, cursor: "pointer", fontFamily: font, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8, minHeight: 160 }}><I d={ic.plus} size={24} color={T.border} /><span style={{ fontSize: 13, fontWeight: 600, color: T.textSec }}>{it ? "Nuovo passaporto" : "New passport"}</span></button>
        </div>
      </div>
    </div>
  );
}

// ─── PROJECTS ─────────────────────────────────────────────
// A Project collects multiple DPPs (Model, Batch, Item) for a building/order.
// Foundation for the Building Digital Logbook (EPBD Art. 19).
function ProjectsView({ onNavigate, L, products = [] }) {
  const it = L?.lang === "it";
  const [showCreate, setShowCreate] = useState(false);
  const [projName, setProjName] = useState("");
  const [projClient, setProjClient] = useState("");
  const [searchProj, setSearchProj] = useState("");
  const [selectedProject, setSelectedProject] = useState(null);

  // Demo projects (will be replaced with real state when persistence is added)
  const projects = [
    { name: "Villa Marchetti — Rimini", client: "Arch. Studio Marchetti", dpps: 12, status: "active", tags: [{l:"Biomattone HC200",t:"Model"},{l:"PR-2026-047",t:"Batch"},{l:"#SN-047-001",t:"Item"},{l:"Serramento 3G",t:"Model"},{l:"#SRR-001",t:"Item"},{l:"#SRR-002",t:"Item"}] },
    { name: "Edificio Verde — Bologna", client: "GreenBuild Srl", dpps: 8, status: "active", tags: [{l:"Biomattone HC200",t:"Model"},{l:"PR-2026-031",t:"Batch"},{l:"Malta M15",t:"Model"}] },
    { name: "Residenza Sole — Modena", client: "Cooperativa Abitare", dpps: 5, status: "draft", tags: [{l:"Biomattone HC200",t:"Model"},{l:"PR-2025-412",t:"Batch"}] },
  ];
  const filtered = projects.filter(p => !searchProj || p.name.toLowerCase().includes(searchProj.toLowerCase()) || p.client.toLowerCase().includes(searchProj.toLowerCase()));
  return (
    <div style={{ fontFamily: font, minHeight: "100vh", display: "flex" }}>
      <Sidebar activePage="projects" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, overflowY: "auto", background: T.bgSoft }}>
        <div style={{ padding: "16px 28px", background: T.bg, borderBottom: `1px solid ${T.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div><h1 style={{ fontSize: 22, fontWeight: 800, color: T.navy }}>{it?"Progetti":"Projects"}</h1><p style={{ fontSize: 13, color: T.textSec, marginTop: 2 }}>{it?"Raccogli DPP per progetto — Building Digital Logbook":"Collect DPPs by project — Building Digital Logbook"}</p></div>
          <Btn primary small onClick={()=>setShowCreate(!showCreate)} style={{ fontSize: 12, padding: "8px 18px" }}><I d={ic.plus} size={13} color={T.navy} /> {it?"Nuovo Progetto":"New Project"}</Btn>
        </div>
        <div style={{ padding: "24px 28px" }}>
          {showCreate && (<div style={{ padding: "20px", borderRadius: 10, border: `1px solid ${T.accent}30`, background: T.accentSoft+"20", marginBottom: 20 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: T.navy, marginBottom: 12 }}>{it?"Nuovo Progetto":"New Project"}</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
              <div><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Nome Progetto *":"Project Name *"}</div><input value={projName} onChange={e=>setProjName(e.target.value)} placeholder={it?"Es. Villa Marchetti — Rimini":"E.g. Villa Marchetti — Rimini"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} /></div>
              <div><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Numero commessa":"Order number"}</div><input placeholder={it?"Es. COM-2026-047":"E.g. ORD-2026-047"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} /></div>
            </div>
            <div style={{ marginBottom: 10 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 4 }}>{it?"Cliente":"Client"}</div><input value={projClient} onChange={e=>setProjClient(e.target.value)} placeholder={it?"Es. Arch. Studio Marchetti":"E.g. Arch. Studio Marchetti"} style={{ width: "100%", padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.border}`, fontSize: 12, fontFamily: font, outline: "none" }} />
            </div>
            <div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, marginBottom: 6 }}>{it?"Seleziona DPP da associare al progetto":"Select DPPs to associate with the project"}</div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 10px", borderRadius: 7, border: `1px solid ${T.border}`, background: T.bg, marginBottom: 8 }}><I d={ic.search} size={12} color={T.textSec} /><input placeholder={it?"Cerca DPP Model, Batch o Item...":"Search DPP Model, Batch or Item..."} style={{ flex: 1, border: "none", outline: "none", fontSize: 11, background: "transparent", fontFamily: font }} /></div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
              {[{l:"Biomattone HC200",t:"Model"},{l:"PR-2026-047",t:"Batch"},{l:"Serramento 3G",t:"Model"}].map((d,i)=>(<div key={i} style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 8px", borderRadius: 5, background: d.t==="Model"?T.bgSoft:d.t==="Batch"?T.accentSoft:T.blueSoft||"#EFF6FF", fontSize: 10, fontWeight: 600, color: d.t==="Model"?T.textSec:d.t==="Batch"?T.accentDark||T.accent:"#3B82F6" }}>{d.l} <span style={{ opacity: 0.6 }}>{d.t}</span> <span style={{ cursor: "pointer", marginLeft: 2 }}>&times;</span></div>))}
            </div>
            <Btn primary onClick={()=>setShowCreate(false)} disabled={!projName}><I d={ic.check} size={14} color={T.navy} /> {it?"Crea Progetto":"Create Project"}</Btn>
          </div>)}

          <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 12px", borderRadius: 8, border: `1px solid ${T.border}`, background: T.bg, marginBottom: 16, maxWidth: 300 }}><I d={ic.search} size={14} color={T.textSec} /><input value={searchProj} onChange={e=>setSearchProj(e.target.value)} placeholder={it?"Cerca progetti...":"Search projects..."} style={{ flex: 1, border: "none", outline: "none", fontSize: 13, background: "transparent", fontFamily: font }} /></div>

          {filtered.map((pr,i)=>(<div key={i}>
            <div style={{ borderRadius: 10, border: `1px solid ${selectedProject===i?T.accent:T.border}`, background: T.bg, padding: "16px 18px", marginBottom: selectedProject===i?0:10, cursor: "pointer", transition: "border-color 0.15s", borderBottomLeftRadius: selectedProject===i?0:10, borderBottomRightRadius: selectedProject===i?0:10 }} onMouseEnter={e=>{if(selectedProject!==i)e.currentTarget.style.borderColor=T.accent}} onMouseLeave={e=>{if(selectedProject!==i)e.currentTarget.style.borderColor=T.border}} onClick={()=>setSelectedProject(selectedProject===i?null:i)}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div><div style={{ fontSize: 15, fontWeight: 700, color: T.navy }}>{pr.name}</div><div style={{ fontSize: 12, color: T.textSec, marginTop: 2 }}>{it?"Cliente":"Client"}: {pr.client} {" · "} {pr.dpps} DPP</div></div>
                <Badge color={pr.status==="active"?T.accentDark||T.accent:T.amber} bg={pr.status==="active"?T.accentSoft:T.amberSoft}>{pr.status==="active"?(it?"Attivo":"Active"):(it?"Bozza":"Draft")}</Badge>
              </div>
              <div style={{ display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" }}>
                {pr.tags.slice(0,4).map((tg,j)=>(<span key={j} style={{ padding: "2px 7px", borderRadius: 4, fontSize: 10, fontWeight: 600, background: tg.t==="Model"?T.bgSoft:tg.t==="Batch"?T.accentSoft:T.blueSoft||"#EFF6FF", color: tg.t==="Model"?T.textSec:tg.t==="Batch"?T.accentDark||T.accent:"#3B82F6" }}>{tg.l} <span style={{ opacity: 0.5 }}>{tg.t}</span></span>))}
                {pr.dpps > 4 && <span style={{ padding: "2px 7px", borderRadius: 4, fontSize: 10, fontWeight: 600, background: T.bgSoft, color: T.textSec }}>+{pr.dpps - 4} {it?"altri":"more"}</span>}
              </div>
            </div>
            {selectedProject===i && (<div style={{ border: `1px solid ${T.accent}`, borderTop: "none", borderBottomLeftRadius: 10, borderBottomRightRadius: 10, background: T.accentSoft+"12", padding: "14px 18px", marginBottom: 10 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: T.textSec, textTransform: "uppercase", marginBottom: 8 }}>{it?"DPP nel progetto":"DPPs in project"} ({pr.dpps})</div>
              {pr.tags.map((tg,j)=>(<div key={j} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.borderLight}`, background: T.bg, marginBottom: 4 }}>
                <div style={{ width: 7, height: 7, borderRadius: "50%", background: tg.t==="Model"?T.navy:tg.t==="Batch"?T.accent:"#3B82F6" }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: T.textDark, flex: 1 }}>{tg.l}</span>
                <Badge color={tg.t==="Model"?T.textSec:tg.t==="Batch"?(T.accentDark||T.accent):"#3B82F6"} bg={tg.t==="Model"?T.bgSoft:tg.t==="Batch"?T.accentSoft:(T.blueSoft||"#EFF6FF")}>{tg.t}</Badge>
              </div>))}
              {pr.dpps > pr.tags.length && <div style={{ fontSize: 11, color: T.textSec, textAlign: "center", padding: 6 }}>+{pr.dpps-pr.tags.length} {it?"altri DPP":"more DPPs"}</div>}
              <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                <Btn small style={{ flex: 1, justifyContent: "center" }}><I d={ic.download} size={12} color={T.textSec} /> {it?"Esporta":"Export"}</Btn>
                <Btn small style={{ flex: 1, justifyContent: "center" }}><I d={ic.plus} size={12} color={T.textSec} /> {it?"Aggiungi DPP":"Add DPP"}</Btn>
              </div>
            </div>)}
          </div>))}

          <div style={{ padding: "10px 14px", borderRadius: 8, background: T.accentSoft+"40", border: `1px solid ${T.accent}30`, fontSize: 11, color: T.textSec, marginTop: 16, display: "flex", alignItems: "center", gap: 8 }}><I d={ic.shield} size={12} color={T.accentDark||T.accent} />{it?"I Progetti raccolgono DPP (Model, Batch, Item) per commessa/edificio. Base per il Building Digital Logbook (EPBD Art. 19). Export unico di tutti i DPP del progetto.":"Projects collect DPPs (Model, Batch, Item) by building/client. Foundation for the Building Digital Logbook (EPBD Art. 19). Single export of all project DPPs."}</div>
        </div>
      </div>
    </div>
  );
}

// ─── DOCUMENTS ────────────────────────────────────────────
function DocumentsView({ onNavigate, L }) {
  const it = L?.lang === "it";
  const [filter, setFilter] = useState("all");
  const docs = [
    { name: "ISO 9001:2015 — Certificato", type: "aziendale", linked: ["Biomattone HC200", "Malta M15", "Serramento Legno"], date: "10 Jan 2026", size: "0.8 MB" },
    { name: "Registrazione REACH", type: "aziendale", linked: ["Biomattone HC200", "Malta M15"], date: "5 Feb 2026", size: "0.3 MB" },
    { name: "DoP-HC200-2025.pdf", type: "prodotto", linked: ["Biomattone HC200"], date: "18 Feb 2026", size: "2.4 MB" },
    { name: "Scheda-Tecnica-M15.pdf", type: "prodotto", linked: ["Malta M15"], date: "12 Feb 2026", size: "1.8 MB" },
    { name: "EPD-HC200-2025.pdf", type: "prodotto", linked: ["Biomattone HC200"], date: "15 Feb 2026", size: "3.1 MB" },
  ];
  const filtered = filter === "all" ? docs : docs.filter(d => d.type === filter);
  return (
    <div style={{ fontFamily: font, minHeight: "100vh", display: "flex" }}>
      <Sidebar activePage="documents" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, padding: "32px 40px", overflowY: "auto", background: T.bgSoft }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}><div><h1 style={{ fontSize: 24, fontWeight: 800, color: T.navy, marginBottom: 4 }}>{it ? "Documenti" : "Documents"}</h1><p style={{ fontSize: 13, color: T.textSec }}>{it ? "Archivio aziendale e documenti di prodotto" : "Company archive and product documents"}</p></div><Btn primary small style={{ fontSize: 12, padding: "8px 18px" }}><I d={ic.upload} size={13} color={T.navy} /> {it ? "Carica documento" : "Upload document"}</Btn></div>
        <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>{[["all", it ? "Tutti" : "All"], ["aziendale", it ? "Aziendali" : "Company"], ["prodotto", it ? "Di prodotto" : "Product"]].map(([k, l]) => (<button key={k} onClick={() => setFilter(k)} style={{ padding: "6px 16px", borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: "pointer", fontFamily: font, border: `1px solid ${filter === k ? T.accent : T.border}`, background: filter === k ? T.accentSoft : T.bg, color: filter === k ? T.accentDark : T.textSec }}>{l}</button>))}</div>
        <div style={{ background: T.bg, borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 100px 200px 90px 70px", padding: "10px 18px", borderBottom: `1px solid ${T.border}`, background: T.bgSoft }}>{[it ? "Documento" : "Document", it ? "Tipo" : "Type", it ? "Collegato a" : "Linked to", it ? "Data" : "Date", it ? "Peso" : "Size"].map((h, i) => <div key={i} style={{ fontSize: 10, fontWeight: 700, color: T.textSec, textTransform: "uppercase", letterSpacing: "0.04em" }}>{h}</div>)}</div>
          {filtered.map((d, i) => (<div key={i} style={{ display: "grid", gridTemplateColumns: "1fr 100px 200px 90px 70px", padding: "12px 18px", borderBottom: i < filtered.length - 1 ? `1px solid ${T.borderLight}` : "none", alignItems: "center" }}><div style={{ display: "flex", alignItems: "center", gap: 8 }}><I d={ic.file} size={14} color={T.accentDark} /><span style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{d.name}</span></div><Badge color={d.type === "aziendale" ? T.accentDark : T.textSec} bg={d.type === "aziendale" ? T.accentSoft : T.bgSoft} style={{ fontSize: 9 }}>{d.type === "aziendale" ? (it ? "Aziendale" : "Company") : (it ? "Prodotto" : "Product")}</Badge><div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>{d.linked.map((l, j) => <span key={j} style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, background: T.bgSoft, color: T.textSec, border: `1px solid ${T.borderLight}` }}>{l}</span>)}</div><span style={{ fontSize: 11, color: T.textSec }}>{d.date}</span><span style={{ fontSize: 11, color: T.textSec }}>{d.size}</span></div>))}
        </div>
        <div style={{ marginTop: 24, padding: "20px 24px", borderRadius: 10, background: T.bg, border: `1px dashed ${T.accent}` }}><h3 style={{ fontSize: 14, fontWeight: 700, color: T.navy, marginBottom: 6 }}>{it ? "Documenti aziendali" : "Company documents"}</h3><p style={{ fontSize: 12, color: T.textSec, lineHeight: 1.6 }}>{it ? "Carica certificazioni aziendali (ISO, REACH, politiche ambientali) e verranno collegati automaticamente a tutti i tuoi passaporti." : "Upload company certifications (ISO, REACH, environmental policies) and they'll be automatically linked to all your passports."}</p></div>
      </div>
    </div>
  );
}

// ─── TEAM ─────────────────────────────────────────────────
function TeamView({ onNavigate, L }) {
  const it = L?.lang === "it";
  const [emails, setEmails] = useState([]);
  const [input, setInput] = useState("");
  const [sent, setSent] = useState(false);
  const addEmail = () => { if (input.includes("@")) { setEmails([...emails, input]); setInput(""); } };
  const sendAll = () => { if (window.posthog) window.posthog.capture("team_invites_sent", { emails }); setSent(true); };
  return (
    <div style={{ fontFamily: font, minHeight: "100vh", display: "flex" }}>
      <Sidebar activePage="team" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, padding: "32px 40px", overflowY: "auto", background: T.bgSoft }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: T.navy, marginBottom: 4 }}>Team</h1>
        <p style={{ fontSize: 13, color: T.textSec, marginBottom: 28 }}>{it ? "Invita i colleghi della tua azienda a collaborare sui passaporti digitali." : "Invite colleagues to collaborate on digital passports."}</p>
        <div style={{ maxWidth: 520 }}>
          <div style={{ padding: "28px 32px", borderRadius: 12, background: T.bg, border: `1px solid ${T.border}`, marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.users} size={18} color={T.accent} /></div><div><div style={{ fontSize: 15, fontWeight: 700, color: T.navy }}>{it ? "Invita il tuo team" : "Invite your team"}</div><div style={{ fontSize: 12, color: T.textSec }}>{it ? "Responsabile qualità, ufficio tecnico, commerciale..." : "Quality manager, technical office, sales..."}</div></div></div>
            {sent ? (<div style={{ textAlign: "center", padding: "20px 0" }}><I d={ic.check} size={28} color={T.accent} /><p style={{ fontSize: 14, fontWeight: 700, color: T.navy, marginTop: 10 }}>{it ? "Inviti registrati!" : "Invites registered!"}</p><p style={{ fontSize: 12, color: T.textSec, marginTop: 4 }}>{it ? "Ti avviseremo quando la funzionalità Team sarà attiva." : "We'll notify you when Team is active."}</p></div>) : (<>
              <div style={{ display: "flex", gap: 8, marginBottom: 12 }}><input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addEmail()} placeholder={it ? "email.collega@azienda.it" : "colleague@company.com"} style={{ flex: 1, padding: "10px 12px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 13, outline: "none", fontFamily: font, boxSizing: "border-box" }} /><Btn onClick={addEmail} small style={{ fontSize: 12, padding: "8px 16px" }}><I d={ic.plus} size={13} color={T.textDark} /> {it ? "Aggiungi" : "Add"}</Btn></div>
              {emails.length > 0 && <div style={{ marginBottom: 14 }}>{emails.map((e, i) => (<div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 10px", borderRadius: 6, background: T.bgSoft, marginBottom: 4 }}><span style={{ fontSize: 12, color: T.textDark }}>{e}</span><button onClick={() => setEmails(emails.filter((_, j) => j !== i))} style={{ background: "none", border: "none", cursor: "pointer", padding: 2 }}><I d={ic.x} size={12} color={T.textSec} /></button></div>))}</div>}
              <Btn primary onClick={sendAll} style={{ width: "100%", justifyContent: "center", opacity: emails.length > 0 ? 1 : 0.4 }}>{it ? "Invia inviti" : "Send invites"} <I d={ic.arrow} size={14} color={T.navy} /></Btn>
            </>)}
          </div>
          <div style={{ padding: "18px 24px", borderRadius: 10, background: T.bg, border: `1px solid ${T.border}` }}><div style={{ fontSize: 13, fontWeight: 700, color: T.navy, marginBottom: 6 }}>{it ? "Membri attuali" : "Current members"}</div><div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 0" }}><div style={{ width: 28, height: 28, borderRadius: "50%", background: T.accentDark, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: T.text }}>AP</div><div><div style={{ fontSize: 12, fontWeight: 600, color: T.textDark }}>A. Pracucci</div><div style={{ fontSize: 10, color: T.textSec }}>a.pracucci@levery.it · Admin</div></div></div></div>
        </div>
      </div>
    </div>
  );
}

// ─── SETTINGS ─────────────────────────────────────────────
function SettingsView({ onNavigate, L }) {
  const it = L?.lang === "it";
  const [company, setCompany] = useState({ name: "", vat: "", address: "", website: "", email: "", phone: "" });
  // Personal account stays static until authentication/users land.
  const [profile, setProfile] = useState({ name: "Alessandro Pracucci", email: "a.pracucci@levery.it", role: "Admin" });
  const [saved, setSaved] = useState(false);
  const [companySaved, setCompanySaved] = useState(false);

  // Load the real company profile from the backend.
  useEffect(() => {
    fetch("/api/company", { credentials: "include" })
      .then(r => r.json())
      .then(c => { if (c && !c.error) setCompany({ name: c.name || "", vat: c.vat || "", address: c.address || "", website: c.website || "", email: c.email || "", phone: c.phone || "" }); })
      .catch(() => {});
  }, []);

  const saveCompany = async () => {
    try {
      await fetch("/api/company", { method: "PATCH", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(company) });
      setCompanySaved(true); setTimeout(() => setCompanySaved(false), 2000);
    } catch { /* ignore */ }
  };
  const save = () => { setSaved(true); setTimeout(() => setSaved(false), 2000); };
  const field = (label, key, obj, setObj, type = "text") => (<div style={{ marginBottom: 16 }}><label style={{ fontSize: 11, fontWeight: 600, color: T.textSec, display: "block", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>{label}</label><input type={type} value={obj[key]} onChange={(e) => setObj({ ...obj, [key]: e.target.value })} style={{ width: "100%", padding: "10px 12px", borderRadius: 6, border: `1px solid ${T.border}`, fontSize: 13, outline: "none", boxSizing: "border-box", fontFamily: font, background: T.bg }} /></div>);
  return (
    <div style={{ fontFamily: font, minHeight: "100vh", display: "flex" }}>
      <Sidebar activePage="settings" onNavigate={onNavigate} L={L} />
      <div style={{ flex: 1, padding: "32px 40px", overflowY: "auto", background: T.bgSoft }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: T.navy, marginBottom: 4 }}>{it ? "Impostazioni" : "Settings"}</h1>
        <p style={{ fontSize: 13, color: T.textSec, marginBottom: 28 }}>{it ? "Gestisci il profilo aziendale e le preferenze dell'account." : "Manage company profile and account preferences."}</p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, maxWidth: 860 }}>
          <div>
            <div style={{ padding: "24px 28px", borderRadius: 12, background: T.bg, border: `1px solid ${T.border}`, marginBottom: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.factory} size={18} color={T.accent} /></div><h2 style={{ fontSize: 16, fontWeight: 700, color: T.navy }}>{it ? "Profilo azienda" : "Company profile"}</h2></div>
              <p style={{ fontSize: 12, color: T.textSec, marginBottom: 16, lineHeight: 1.5 }}>{it ? "Questi dati appaiono nei passaporti pubblicati come informazioni del produttore." : "This data appears in published passports as manufacturer information."}</p>
              {field(it ? "Ragione sociale" : "Company name", "name", company, setCompany)}{field("P.IVA / VAT", "vat", company, setCompany)}{field(it ? "Indirizzo sede" : "Registered address", "address", company, setCompany)}{field(it ? "Sito web" : "Website", "website", company, setCompany, "url")}{field("Email", "email", company, setCompany, "email")}{field(it ? "Telefono" : "Phone", "phone", company, setCompany, "tel")}
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 4 }}><Btn primary onClick={saveCompany} small style={{ fontSize: 12, padding: "8px 20px" }}>{it ? "Salva modifiche" : "Save changes"} <I d={ic.check} size={13} color={T.navy} /></Btn>{companySaved && <span style={{ fontSize: 12, color: T.accent, fontWeight: 600 }}>{it ? "Salvato ✓" : "Saved ✓"}</span>}</div>
            </div>
          </div>
          <div>
            <div style={{ padding: "24px 28px", borderRadius: 12, background: T.bg, border: `1px solid ${T.border}`, marginBottom: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.users} size={18} color={T.accent} /></div><h2 style={{ fontSize: 16, fontWeight: 700, color: T.navy }}>{it ? "Account personale" : "Personal account"}</h2></div>
              {field(it ? "Nome completo" : "Full name", "name", profile, setProfile)}{field("Email", "email", profile, setProfile, "email")}
              <div style={{ marginBottom: 16 }}><label style={{ fontSize: 11, fontWeight: 600, color: T.textSec, display: "block", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.04em" }}>{it ? "Lingua" : "Language"}</label><div style={{ display: "flex", gap: 6 }}>{[["it", "Italiano"], ["en", "English"]].map(([k, l]) => (<button key={k} onClick={() => L.setLang(k)} style={{ padding: "8px 16px", borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: "pointer", fontFamily: font, border: `1px solid ${L.lang === k ? T.accent : T.border}`, background: L.lang === k ? T.accentSoft : T.bg, color: L.lang === k ? T.accentDark : T.textSec }}>{l}</button>))}</div></div>
              <Btn primary onClick={save} small style={{ fontSize: 12, padding: "8px 20px" }}>{it ? "Aggiorna profilo" : "Update profile"} <I d={ic.check} size={13} color={T.navy} /></Btn>
            </div>
            <div style={{ padding: "20px 28px", borderRadius: 12, background: T.bg, border: `1px solid ${T.border}`, marginBottom: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.chart} size={18} color={T.accent} /></div><h2 style={{ fontSize: 16, fontWeight: 700, color: T.navy }}>{it ? "Piano e fatturazione" : "Plan & billing"}</h2></div>
              <div style={{ padding: "12px 16px", borderRadius: 8, background: T.bgSoft, display: "flex", justifyContent: "space-between", alignItems: "center" }}><div><div style={{ fontSize: 13, fontWeight: 700, color: T.navy }}>Starter</div><div style={{ fontSize: 11, color: T.textSec }}>{it ? "3 passaporti attivi" : "3 active passports"}</div></div><Badge color={T.accent} bg={T.accentSoft}>{it ? "Attivo" : "Active"}</Badge></div>
            </div>
            <div style={{ padding: "20px 28px", borderRadius: 12, background: T.bg, border: `1px solid ${T.border}`, opacity: 0.6 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.bolt} size={18} color={T.accent} /></div><h2 style={{ fontSize: 16, fontWeight: 700, color: T.navy }}>{it ? "Integrazioni" : "Integrations"}</h2></div>
              <p style={{ fontSize: 12, color: T.textSec }}>{it ? "API, webhook e collegamento ERP — disponibile a breve." : "API, webhooks and ERP integration — coming soon."}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ━━━ NEW LANDING ━━━
// ─── THEME ───
const $T = {
  navy: "#0B1D3A", navyMid: "#122A4E", navyLight: "#1A3562",
  accent: "#2EC4A0", accentHover: "#26A88A", accentSoft: "rgba(46,196,160,0.08)", accentBorder: "rgba(46,196,160,0.2)",
  white: "#FFFFFF", bg: "#F8FAFB", bgSoft: "#F1F4F7",
  text: "#E8ECF1", textMuted: "#94A3B8", textDark: "#1E293B", textSec: "#64748B",
  border: "#E2E8F0", borderLight: "#F1F5F9", warn: "#E87C3E",
};

// ─── POSTHOG TRACKING ───
const $track = (event, data = {}) => {
  if (window.posthog) window.posthog.capture(event, data);
  console.log("[track]", event, data);
};

// ─── SVG ICON ───
const $I = ({ d, size = 20, color = "currentColor", style = {} }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" style={style}>
    {d.split("M").filter(Boolean).map((seg, i) => <path key={i} d={`M${seg}`} />)}
  </svg>
);
const $ic = {
  link: "M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71",
  grid: "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
  trophy: "M6 9H4.5a2.5 2.5 0 0 1 0-5H6M18 9h1.5a2.5 2.5 0 0 0 0-5H18M6 9v4a6 6 0 0 0 12 0V9M9 21h6M12 17v4",
  refresh: "M1 4v6h6M23 20v-6h-6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4-4.64 4.36A9 9 0 0 1 3.51 15",
  fileCheck: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M9 15l2 2 4-4",
  puzzle: "M20 7h-3a2 2 0 0 1-2-2V2M9 22a1 1 0 0 1-1-1v-3H5a2 2 0 0 1-2-2v-3h3a1 1 0 0 0 0-2H3V8a2 2 0 0 1 2-2h3V3a1 1 0 0 0 2 0v3h3a2 2 0 0 1 2 2v3h-3a1 1 0 0 0 0 2h3v3a2 2 0 0 1-2 2h-3v3a1 1 0 0 0 2 0z",
  upload: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12",
  search: "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.35-4.35",
  share: "M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13",
  shield: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
  check: "M20 6L9 17l-5-5",
  arrow: "M5 12h14M12 5l7 7-7 7",
  chevDown: "M6 9l6 6 6-6",
  chevUp: "M18 15l-6-6-6 6",
  globe: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z",
  building: "M3 21h18M3 7v14M21 7v14M6 11h2M6 15h2M10 11h2M10 15h2M14 11h2M14 15h2M18 11h2M18 15h2M3 7l9-4 9 4",
  x: "M18 6L6 18M6 6l12 12",
  menu: "M3 12h18M3 6h18M3 18h18",
  mail: "M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zM22 6l-10 7L2 6",
  award: "M12 15l-3.5 2 1-3.9L6 10h4L12 6l2 4h4l-3.5 3.1 1 3.9z",
};

// ─── COMPONENTS ───
const $Badge = ({ children, bg = $T.accentSoft, color = $T.accent, style = {} }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "5px 14px", borderRadius: 20, background: bg, color, fontSize: 11, fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase", ...style }}>{children}</span>
);

const $Btn = ({ children, primary, style = {}, ...props }) => {
  const [h, setH] = useState(false);
  const base = primary
    ? { background: h ? $T.accentHover : $T.accent, color: $T.navy, border: "none", fontWeight: 700 }
    : { background: h ? $T.bgSoft : $T.white, color: $T.navy, border: `1px solid ${$T.border}`, fontWeight: 600 };
  return (
    <button onMouseEnter={() => setH(true)} onMouseLeave={() => setH(false)}
      style={{ padding: "12px 28px", borderRadius: 10, fontSize: 14, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 8, transition: "all 0.2s", fontFamily: "inherit", ...base, ...style }} {...props}>
      {children}
    </button>
  );
};

// ─── SCROLL TRACKING ───
const $useScrollDepth = () => {
  const tracked = useRef(new Set());
  useEffect(() => {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting && !tracked.current.has(e.target.id)) { tracked.current.add(e.target.id); $track("section_viewed", { section: e.target.id }); } });
    }, { threshold: 0.3 });
    document.querySelectorAll("[data-track-section]").forEach((el) => obs.observe(el));
    return () => obs.disconnect();
  }, []);
};

// ─── FEATURE VISUAL EXAMPLES ───
const $featEx = {
  it: [
    { type: "before_after", before: ["📎 Scheda_tecnica_v3.pdf", "📎 DoP_2024.pdf", "📎 EPD_certificato.pdf", "📎 report_laboratorio.xlsx", "📎 foto_catalogo.jpg"], after: "🔗 deeppy.eu/p/biomattone-hc200", caption: "Un link al posto di tanti allegati. Sempre aggiornato." },
    { type: "profile", caption: "Il tuo prodotto, presentato in modo ordinato e professionale." },
    { type: "spec", quote: "\"Isolamento termico con EPD verificata, GWP ≤ 5 kg CO₂eq/m², conformità CAM...\"", ok: "Il tuo prodotto è già conforme", label: "Esempio: capitolato LEED" },
    { type: "update", items: ["Link", "QR code", "Sito web"], caption: "Aggiorni una volta. Tutti vedono l'ultima versione." },
    { type: "trace", cols: ["Dato", "Valore", "Fonte"], rows: [["Resistenza termica", "0.035 W/mK", "Scheda tecnica pag. 2"], ["Reazione al fuoco", "B-s1,d0", "DoP pag. 1"], ["GWP (A1-A3)", "3.42 kg CO₂eq", "EPD verificata §6.2"]], caption: "Ogni dato collegato al documento originale." },
    { type: "gaps", items: [["LCA (Life Cycle Assessment)", false], ["Analisi di riciclabilità", false], ["Contenuto di riciclato", false], ["Scheda tecnica", true], ["Dichiarazione di prestazione", true]], caption: "DeePPy ti mostra cosa manca per essere completo.", miss: "Mancante" },
  ],
  en: [
    { type: "before_after", before: ["📎 Technical_sheet_v3.pdf", "📎 DoP_2024.pdf", "📎 EPD_certificate.pdf", "📎 lab_report.xlsx", "📎 catalog_photo.jpg"], after: "🔗 deeppy.eu/p/hemp-brick-hc200", caption: "One link instead of many attachments. Always up to date." },
    { type: "profile", caption: "Your product, presented in an organized, professional way." },
    { type: "spec", quote: "\"Thermal insulation with verified EPD, GWP ≤ 5 kg CO₂eq/m², green procurement compliant...\"", ok: "Your product already complies", label: "Example: LEED specification" },
    { type: "update", items: ["Link", "QR code", "Website"], caption: "Update once. Everyone sees the latest version." },
    { type: "trace", cols: ["Data", "Value", "Source"], rows: [["Thermal resistance", "0.035 W/mK", "Technical sheet p. 2"], ["Fire reaction", "B-s1,d0", "DoP p. 1"], ["GWP (A1-A3)", "3.42 kg CO₂eq", "Verified EPD §6.2"]], caption: "Every data point linked to the original document." },
    { type: "gaps", items: [["LCA (Life Cycle Assessment)", false], ["Recyclability analysis", false], ["Recycled content", false], ["Technical sheet", true], ["Declaration of performance", true]], caption: "DeePPy shows you what's missing to be complete.", miss: "Missing" },
  ],
};

// ─── SAMPLE DPP PRODUCTS (3 distinct) ───
const $products = {
  it: [
    { id: 0, name: "Biomattone HC200", mfr: "Verdecalce Srl", cat: "Muratura bio-based", pct: 82,
      specs: [["Conducibilità termica", "0.07 W/mK"], ["Densità", "350 kg/m³"], ["Spessore", "200 mm"], ["Reazione al fuoco", "Euroclasse B-s1,d0"], ["Resistenza a compressione", "≥ 2.0 MPa"], ["Permeabilità al vapore", "μ = 5"]],
      certs: ["DoP n. 2025-HC200", "Marcatura CE (EN 771)", "CAM Edilizia", "Certificazione bio-based (EN 16785)"],
      env: [["GWP (A1-A3)", "-12.8 kg CO₂eq/m²"], ["Contenuto bio-based", "62%"], ["Contenuto riciclato", "8%"], ["Riciclabilità a fine vita", "—"]],
      missing: ["LCA completa (moduli A4-C4)", "Analisi di riciclabilità", "Scheda SCIP (ECHA)"] },
    { id: 1, name: "Malta Premiscelata M15", mfr: "Grigia Cementi SpA", cat: "Malte per muratura", pct: 91,
      specs: [["Resistenza a compressione", "≥ 15 MPa"], ["Aderenza", "≥ 0.30 MPa"], ["Reazione al fuoco", "Euroclasse A1"], ["Assorbimento capillare", "W0"], ["Tempo di lavorabilità", "60 min"], ["Granulometria", "0-2 mm"]],
      certs: ["DoP n. 2024-M15P", "Marcatura CE (EN 998-2)", "ISO 9001:2015", "EPD verificata (IBU)"],
      env: [["GWP (A1-A3)", "0.18 kg CO₂eq/kg"], ["Contenuto riciclato", "15%"], ["Energia primaria", "1.2 MJ/kg"], ["Riciclabilità a fine vita", "Inerte — conferimento in discarica"]],
      missing: ["Scheda SCIP (ECHA)"] },
    { id: 2, name: "Serramento Legno Lamellare", mfr: "Nordinfissi Srl", cat: "Serramenti", pct: 68,
      specs: [["Trasmittanza termica Uw", "1.0 W/m²K"], ["Essenza", "Abete lamellare"], ["Spessore telaio", "78 mm"], ["Classe permeabilità aria", "Classe 4"], ["Tenuta acqua", "E 750"], ["Resistenza al vento", "C5"]],
      certs: ["DoP n. 2025-SLL78", "Marcatura CE (EN 14351-1)", "FSC-C098765"],
      env: [["GWP (A1-A3)", "—"], ["Contenuto bio-based", "85%"], ["Contenuto riciclato", "—"], ["EPD", "—"]],
      missing: ["EPD (Environmental Product Declaration)", "LCA completa", "Analisi di riciclabilità", "Dati di fine vita", "Contenuto riciclato"] },
  ],
  en: [
    { id: 0, name: "Hemp Brick HC200", mfr: "Verdecalce Srl", cat: "Bio-based masonry", pct: 82,
      specs: [["Thermal conductivity", "0.07 W/mK"], ["Density", "350 kg/m³"], ["Thickness", "200 mm"], ["Fire reaction", "Euroclass B-s1,d0"], ["Compressive strength", "≥ 2.0 MPa"], ["Vapour permeability", "μ = 5"]],
      certs: ["DoP no. 2025-HC200", "CE Marking (EN 771)", "Green Public Procurement", "Bio-based certification (EN 16785)"],
      env: [["GWP (A1-A3)", "-12.8 kg CO₂eq/m²"], ["Bio-based content", "62%"], ["Recycled content", "8%"], ["End-of-life recyclability", "—"]],
      missing: ["Complete LCA (modules A4-C4)", "Recyclability analysis", "SCIP datasheet (ECHA)"] },
    { id: 1, name: "Premixed Mortar M15", mfr: "Grigia Cementi SpA", cat: "Masonry mortar", pct: 91,
      specs: [["Compressive strength", "≥ 15 MPa"], ["Adhesion", "≥ 0.30 MPa"], ["Fire reaction", "Euroclass A1"], ["Capillary absorption", "W0"], ["Working time", "60 min"], ["Grain size", "0-2 mm"]],
      certs: ["DoP no. 2024-M15P", "CE Marking (EN 998-2)", "ISO 9001:2015", "Verified EPD (IBU)"],
      env: [["GWP (A1-A3)", "0.18 kg CO₂eq/kg"], ["Recycled content", "15%"], ["Primary energy", "1.2 MJ/kg"], ["End-of-life recyclability", "Inert — landfill disposal"]],
      missing: ["SCIP datasheet (ECHA)"] },
    { id: 2, name: "Laminated Wood Window", mfr: "Nordinfissi Srl", cat: "Windows & doors", pct: 68,
      specs: [["Thermal transmittance Uw", "1.0 W/m²K"], ["Wood species", "Laminated spruce"], ["Frame depth", "78 mm"], ["Air permeability class", "Class 4"], ["Water tightness", "E 750"], ["Wind resistance", "C5"]],
      certs: ["DoP no. 2025-SLL78", "CE Marking (EN 14351-1)", "FSC-C098765"],
      env: [["GWP (A1-A3)", "—"], ["Bio-based content", "85%"], ["Recycled content", "—"], ["EPD", "—"]],
      missing: ["EPD (Environmental Product Declaration)", "Complete LCA", "Recyclability analysis", "End-of-life data", "Recycled content"] },
  ],
};

// ─── i18n COPY ───
const $tx = {
  it: {
    nav: { feat: "Funzionalità", how: "Come funziona", plans: "Piano", login: "Login", cta: "Richiedi accesso" },
    hero: { badge: "ESPR EU 2024/1781 Ready", h1: "Il passaporto digitale dei tuoi\nprodotti da costruzione.", sub: "Tutte le informazioni tecniche in un unico posto, sempre aggiornate, condivisibili con un link.", body: "Risparmi tempo eliminando le richieste ripetitive. Ti presenti in modo ordinato e professionale. Con DeePPy hai il pieno controllo delle tue informazioni tecniche: i dati vengono organizzati automaticamente, ma sei tu a validare ogni informazione.", cta1: "Richiedi accesso", cta2: "Scopri come funziona" },
    feat: { title: "Perché i produttori scelgono DeePPy", items: [
      { ic: "link", tag: "Efficienza", h: "Da tanti file sparsi a un unico link.", p: "Quando un progettista o un'impresa ti chiede la documentazione tecnica, mandi un link. Non cerchi più file tra cartelle e email. Non interrompi quello che stai facendo." },
      { ic: "grid", tag: "Immagine", h: "Tutte le informazioni di prodotto, ordinate e organizzate.", p: "QR code per i tuoi prodotti e per i cataloghi. Quando un progettista o un'impresa apre il tuo link, trova tutto ordinato, strutturato e aggiornato — non una cartella di allegati da scaricare." },
      { ic: "trophy", tag: "Competitività", h: "Chi ha le informazioni tecniche pronte viene scelto prima.", p: "Nei capitolati LEED, BREEAM e negli appalti pubblici con CAM, chi ha documentazione strutturata e accessibile parte in vantaggio. Con DeePPy, il tuo prodotto è già dove i progettisti lo cercano." },
      { ic: "refresh", tag: "Aggiornamento", h: "Aggiorna una volta, aggiornato ovunque.", p: "Quando rinnovi una certificazione o aggiorni un dato ambientale, carichi il nuovo documento. Ogni link e QR code si aggiorna. I tuoi clienti vedono sempre l'ultima versione." },
      { ic: "fileCheck", tag: "Tracciabilità", h: "Ogni informazione estratta è collegata al documento originale.", p: "Sai sempre da dove viene ogni dato e puoi verificarlo. Il passaporto del tuo prodotto lo crei tu — sei tu il responsabile delle informazioni che condividi, e con DeePPy ne hai il pieno controllo." },
      { ic: "puzzle", tag: "Completezza", h: "Completa quello che manca.", p: "DeePPy evidenzia le informazioni mancanti per la conformità — come LCA o EPD — e ti permette di richiedere supporto specialistico direttamente dalla piattaforma." },
    ]},
    how: { title: "Come funziona", steps: [
      { ic: "upload", n: "01", h: "Carica i documenti che hai già", p: "Schede tecniche, certificazioni, dichiarazioni di prestazione, dati ambientali, relazioni di prova, distinta materiali. PDF, Excel, immagini — qualsiasi formato." },
      { ic: "search", n: "02", h: "Le informazioni vengono estratte e organizzate", p: "I contenuti vengono mappati automaticamente. Ogni informazione estratta riporta un link al punto esatto del documento originale: verifichi in un istante e confermi.", p2: "Manca qualcosa? DeePPy ti indica esattamente cosa manca e ti guida nel recuperarlo." },
      { ic: "share", n: "03", h: "Pubblica, condividi, fatti trovare", p: "Un link diretto, un QR code per i tuoi prodotti e cataloghi, un'integrazione per il tuo sito web — copia una riga di codice e il passaporto del prodotto è visibile ai tuoi visitatori. Il tuo prodotto parla da solo." },
    ]},
    cred: { levery: "Levery Società Benefit — 10+ anni di esperienza nell'innovazione del settore costruzioni in Italia", reg: "Struttura dati allineata al regolamento ESPR EU 2024/1781 — in vigore per prodotti da costruzione dal 2028" },
    edge: { badge: "ESPR · CPR", h: "Un passo avanti rispetto ai tuoi competitor. Oggi.", p: "I tuoi concorrenti mandano ancora allegati via email. Tu condividi un passaporto digitale completo, verificabile, sempre aggiornato. E quando il DPP diventerà obbligatorio nell'UE (ESPR EU 2024/1781, CPR 2024/3110), tu sarai già pronto — loro no." },
    plan: { h: "Inizia con un prodotto.", sub: "Ogni passaporto digitale include: upload documenti, estrazione automatica delle informazioni, QR code, link condivisibile, pubblicazione nel catalogo DeePPy, supporto email.", cta: "Richiedi accesso", more: "Hai più di 5 prodotti?", moreCta: "Parliamone" },
    catalog: { h: "Prodotti già pubblicati", sub: "Passaporti verificati, consultabili da chiunque. Il tuo prodotto potrebbe essere il prossimo.", note: "Questi sono passaporti dimostrativi" },
    final: { h: "Il tuo prodotto ha già tutti i documenti.\nGli manca solo un posto dove stiano insieme.", cta: "Richiedi accesso" },
    form: { title: "Richiedi accesso a DeePPy", name: "Nome e cognome", company: "Azienda", email: "Email", products: "Quanti prodotti hai a catalogo?", message: "Messaggio (opzionale)", send: "Invia richiesta", thanks: "Grazie! Ti contatteremo a breve.", opts: ["1–10", "11–50", "51–200", "200+"] },
    signup: { title: "Unisciti ai primi produttori", sub: "Lascia i tuoi dati per essere tra i primi ad accedere a DeePPy." },
    dppTabs: ["Dati tecnici", "Certificazioni", "Ambiente", "Mancanti"],
    complete: "Aiutami a completare il passaporto", createYours: "Crea il tuo", exampleNote: "Questo è un passaporto dimostrativo",
    footer: { vision: "Crediamo nella trasparenza della filiera delle costruzioni.", eu: "Questo progetto ha ricevuto finanziamenti dall'Unione Europea (Grant Agreement ID 101136597 e Grant Agreement ID 101091494)." },
    miss: "Mancante", before: "Prima", after: "Dopo", seeEx: "Vedi esempio", close: "Chiudi", updated: "aggiornato",
  },
  en: {
    nav: { feat: "Features", how: "How it works", plans: "Plan", login: "Login", cta: "Request access" },
    hero: { badge: "ESPR EU 2024/1781 Ready", h1: "The digital passport for your\nconstruction products.", sub: "All technical information in one place, always up to date, shareable with a link.", body: "Save time by eliminating repetitive requests. Present yourself in an organized, professional way. With DeePPy you have full control over your technical information: data is organized automatically, but you validate every piece of information.", cta1: "Request access", cta2: "See how it works" },
    feat: { title: "Why manufacturers choose DeePPy", items: [
      { ic: "link", tag: "Efficiency", h: "From scattered files to a single link.", p: "When a specifier or contractor asks for technical documentation, you send a link. No more searching through folders and emails. No more interrupting what you're doing." },
      { ic: "grid", tag: "Image", h: "All product information, organized and structured.", p: "QR code for your products and catalogs. When a specifier or contractor opens your link, they find everything organized, structured and up to date — not a folder of attachments to download." },
      { ic: "trophy", tag: "Competitive", h: "Whoever has the technical information ready gets chosen first.", p: "In LEED and BREEAM specs, and in green public procurement, structured and accessible documentation gives you the edge. With DeePPy, your product is already where specifiers look." },
      { ic: "refresh", tag: "Updates", h: "Update once, updated everywhere.", p: "When you renew a certification or update environmental data, upload the new document. Every link and QR code updates. Your clients always see the latest version." },
      { ic: "fileCheck", tag: "Traceability", h: "Every extracted piece of information is linked to the original document.", p: "You always know where each data point comes from and can verify it. Your product passport is created by you — you are responsible for the information you share, and with DeePPy you have full control." },
      { ic: "puzzle", tag: "Completeness", h: "Complete what's missing.", p: "DeePPy highlights missing information for compliance — such as LCA or EPD — and lets you request specialist support directly from the platform." },
    ]},
    how: { title: "How it works", steps: [
      { ic: "upload", n: "01", h: "Upload documents you already have", p: "Technical sheets, certifications, performance declarations, environmental data, test reports, bill of materials. PDF, Excel, images — any format." },
      { ic: "search", n: "02", h: "Information is extracted and organized", p: "Contents are mapped automatically. Every extracted piece of information includes a link to the exact point in the original document: you verify instantly and confirm.", p2: "Something missing? DeePPy tells you exactly what's needed and guides you through recovering it." },
      { ic: "share", n: "03", h: "Publish, share, get found", p: "A direct link, a QR code for your products and catalogs, an integration for your website — copy one line of code and the product passport is visible to your visitors. Your product speaks for itself." },
    ]},
    cred: { levery: "Levery Società Benefit — 10+ years of experience in construction innovation across Italy, Denmark, Germany, and the EU", reg: "Data structure aligned with ESPR EU 2024/1781 — mandatory for construction products across the EU from 2028" },
    edge: { badge: "ESPR · CPR", h: "One step ahead of your competitors. Today.", p: "Your competitors are still sending attachments by email. You share a complete, verifiable, always up-to-date digital passport. And when DPPs become mandatory in the EU (ESPR EU 2024/1781, CPR 2024/3110), you'll already be ready — they won't." },
    plan: { h: "Start with one product.", sub: "Every digital passport includes: document upload, automatic information extraction, QR code, shareable link, publication in the DeePPy catalog, email support.", cta: "Request access", more: "Have more than 5 products?", moreCta: "Let's talk" },
    catalog: { h: "Published products", sub: "Verified passports, accessible to anyone. Your product could be next.", note: "These are demonstration passports" },
    final: { h: "Your product already has all the documents.\nIt just needs one place to bring them together.", cta: "Request access" },
    form: { title: "Request access to DeePPy", name: "Full name", company: "Company", email: "Email", products: "How many products in your catalog?", message: "Message (optional)", send: "Send request", thanks: "Thank you! We'll be in touch soon.", opts: ["1–10", "11–50", "51–200", "200+"] },
    signup: { title: "Join the first manufacturers", sub: "Leave your details to be among the first to access DeePPy." },
    dppTabs: ["Technical data", "Certifications", "Environment", "Missing"],
    complete: "Help me complete the passport", createYours: "Create yours", exampleNote: "This is a demonstration passport",
    footer: { vision: "We believe in transparency across the construction supply chain.", eu: "This project received funding from the European Union (Grant Agreement ID 101136597 and Grant Agreement ID 101091494)." },
    miss: "Missing", before: "Before", after: "After", seeEx: "See example", close: "Close", updated: "updated",
  },
};

// ─── FORM MODAL ───
const $FormModal = ({ open, onClose, t, context }) => {
  const [form, setForm] = useState({ name: "", company: "", email: "", products: "", message: "" });
  const [sent, setSent] = useState(false);
  if (!open) return null;
  const submit = () => {
    $track("form_submitted", { ...form, context });
    fetch("https://formsubmit.co/ajax/info@deeppy.eu", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({ ...form, context, _subject: "Nuovo lead DeePPy — " + (form.company || form.name || "Anonimo"), _template: "table" }),
    }).catch(console.error);
    setSent(true);
  };
  const inp = (k, ph) => <input value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })} placeholder={ph} style={{ width: "100%", padding: "12px 16px", borderRadius: 8, border: `1px solid ${$T.border}`, fontSize: 14, fontFamily: "inherit", boxSizing: "border-box", outline: "none" }} />;
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(11,29,58,0.6)", backdropFilter: "blur(4px)" }} onClick={onClose}>
      <div style={{ background: $T.white, borderRadius: 16, padding: 36, maxWidth: 440, width: "90%", position: "relative", maxHeight: "90vh", overflowY: "auto" }} onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} style={{ position: "absolute", top: 16, right: 16, background: "none", border: "none", cursor: "pointer" }}><$I d={$ic.x} size={18} color={$T.textSec} /></button>
        {sent ? (
          <div style={{ textAlign: "center", padding: "32px 0" }}>
            <div style={{ width: 56, height: 56, borderRadius: "50%", background: $T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}><$I d={$ic.check} size={28} color={$T.accent} /></div>
            <p style={{ fontSize: 18, fontWeight: 700, color: $T.navy }}>{t.thanks}</p>
          </div>
        ) : (
          <>
            <h3 style={{ fontSize: 20, fontWeight: 800, color: $T.navy, marginBottom: 4 }}>{context === "signup" ? t.title.replace("accesso", "").replace("access", "") : t.title}</h3>
            {context === "signup" && <p style={{ fontSize: 13, color: $T.textSec, marginBottom: 16 }}>{/* signup sub handled by context */}</p>}
            <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 16 }}>
              {inp("name", t.name)}{inp("company", t.company)}{inp("email", t.email)}
              <div>
                <p style={{ fontSize: 12, color: $T.textSec, marginBottom: 6 }}>{t.products}</p>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {t.opts.map((o) => <button key={o} onClick={() => setForm({ ...form, products: o })} style={{ padding: "8px 16px", borderRadius: 8, border: `1px solid ${form.products === o ? $T.accent : $T.border}`, background: form.products === o ? $T.accentSoft : $T.white, color: form.products === o ? $T.accentHover : $T.textSec, fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: "inherit" }}>{o}</button>)}
                </div>
              </div>
              <textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} placeholder={t.message} rows={3} style={{ width: "100%", padding: "12px 16px", borderRadius: 8, border: `1px solid ${$T.border}`, fontSize: 14, fontFamily: "inherit", resize: "vertical", boxSizing: "border-box", outline: "none" }} />
              <$Btn primary onClick={submit} style={{ width: "100%", justifyContent: "center", fontSize: 15, padding: "14px 0" }}>{t.send} <$I d={$ic.arrow} size={16} color={$T.navy} /></$Btn>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// ─── DPP MODAL ───
const $DppModal = ({ lang, prod, activeTab, onTab, onClose, onComplete, onCta, t }) => {
  const tabs = t.dppTabs;
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(11,29,58,0.6)", backdropFilter: "blur(4px)" }} onClick={onClose}>
      <div style={{ background: $T.white, borderRadius: 16, maxWidth: 580, width: "92%", maxHeight: "88vh", overflowY: "auto", position: "relative" }} onClick={(e) => e.stopPropagation()}>
        <div style={{ background: $T.navy, borderRadius: "16px 16px 0 0", padding: "24px 28px", display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: $T.navyLight, display: "flex", alignItems: "center", justifyContent: "center" }}><span style={{ color: $T.accent, fontWeight: 800, fontSize: 11 }}>{prod.name.split(" ")[0].slice(0, 4)}</span></div>
          <div style={{ flex: 1 }}><div style={{ fontSize: 17, fontWeight: 800, color: $T.text }}>{prod.name}</div><div style={{ fontSize: 12, color: $T.textMuted }}>{prod.mfr} · {prod.cat}</div></div>
          <div style={{ width: 44, height: 44, borderRadius: "50%", border: `3px solid ${prod.pct >= 85 ? $T.accent : prod.pct >= 70 ? "#F5A623" : $T.warn}`, display: "flex", alignItems: "center", justifyContent: "center" }}><span style={{ fontSize: 14, fontWeight: 800, color: prod.pct >= 85 ? $T.accent : prod.pct >= 70 ? "#F5A623" : $T.warn }}>{prod.pct}%</span></div>
          <button onClick={onClose} style={{ position: "absolute", top: 16, right: 16, background: "none", border: "none", cursor: "pointer" }}><$I d={$ic.x} size={18} color={$T.textMuted} /></button>
        </div>
        <div style={{ display: "flex", borderBottom: `1px solid ${$T.border}`, padding: "0 28px" }}>
          {tabs.map((tab, j) => <button key={j} onClick={() => onTab(j)} style={{ padding: "12px 14px", fontSize: 12, fontWeight: 600, color: activeTab === j ? $T.accent : $T.textSec, background: "none", border: "none", borderBottom: activeTab === j ? `2px solid ${$T.accent}` : "2px solid transparent", cursor: "pointer", fontFamily: "inherit" }}>{tab}{j === 3 && prod.missing.length > 0 ? ` (${prod.missing.length})` : ""}</button>)}
        </div>
        <div style={{ padding: "20px 28px 28px" }}>
          {activeTab === 0 && <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>{prod.specs.map(([l, v], j) => <div key={j} style={{ padding: "10px 12px", borderRadius: 8, background: $T.bgSoft }}><div style={{ fontSize: 10, color: $T.textSec, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 3 }}>{l}</div><div style={{ fontSize: 14, fontWeight: 700, color: $T.navy }}>{v}</div></div>)}</div>}
          {activeTab === 1 && <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>{prod.certs.map((c, j) => <div key={j} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 8, background: $T.bgSoft }}><$I d={$ic.shield} size={16} color={$T.accent} /><span style={{ fontSize: 13, fontWeight: 600, color: $T.navy, flex: 1 }}>{c}</span><$I d={$ic.check} size={14} color={$T.accent} /></div>)}</div>}
          {activeTab === 2 && <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>{prod.env.map(([l, v], j) => <div key={j} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", borderRadius: 8, background: $T.bgSoft }}><span style={{ fontSize: 13, color: $T.textSec }}>{l}</span><span style={{ fontSize: 14, fontWeight: 700, color: v === "—" ? $T.textMuted : $T.navy }}>{v}</span></div>)}</div>}
          {activeTab === 3 && <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>{prod.missing.map((m, j) => <div key={j} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 8, background: $T.bgSoft }}><div style={{ width: 16, height: 16, borderRadius: "50%", border: `2px solid ${$T.warn}`, opacity: 0.6, flexShrink: 0 }} /><span style={{ fontSize: 13, color: $T.textSec, flex: 1 }}>{m}</span><span style={{ fontSize: 10, color: $T.warn, fontWeight: 600 }}>{t.miss}</span></div>)}<button onClick={onComplete} style={{ marginTop: 8, width: "100%", padding: "12px 0", borderRadius: 10, background: $T.accentSoft, border: `1px solid ${$T.accentBorder}`, color: $T.accent, fontSize: 13, fontWeight: 700, cursor: "pointer", fontFamily: "inherit", display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}><$I d={$ic.puzzle} size={15} color={$T.accent} />{t.complete}</button></div>}
        </div>
        <div style={{ borderTop: `1px solid ${$T.border}`, padding: "14px 28px", display: "flex", justifyContent: "space-between", alignItems: "center" }}><span style={{ fontSize: 11, color: $T.textSec }}>{t.exampleNote}</span><$Btn primary onClick={onCta} style={{ padding: "8px 20px", fontSize: 12 }}>{t.createYours}</$Btn></div>
      </div>
    </div>
  );
};

// ─── FEATURE EXAMPLE PANEL ───
const $FeatPanel = ({ ex, t }) => {
  if (!ex) return null;
  const S = { wrap: { background: $T.white, border: `1px solid ${$T.accent}`, borderRadius: "0 0 14px 14px", padding: 20 }, cap: { fontSize: 11, color: $T.textSec, marginTop: 12, fontStyle: "italic", textAlign: "center" } };
  return (
    <div style={S.wrap}>
      {ex.type === "before_after" && <div style={{ display: "flex", flexDirection: "column", gap: 10 }}><div style={{ background: $T.bgSoft, borderRadius: 8, padding: 12 }}><div style={{ fontSize: 10, fontWeight: 700, color: $T.textSec, textTransform: "uppercase", marginBottom: 6 }}>{t.before}</div>{ex.before.map((f, j) => <div key={j} style={{ fontSize: 12, color: $T.textSec, padding: "2px 0" }}>{f}</div>)}</div><div style={{ textAlign: "center" }}><$I d={$ic.chevDown} size={18} color={$T.accent} /></div><div style={{ background: $T.accentSoft, borderRadius: 8, padding: 12, textAlign: "center" }}><div style={{ fontSize: 10, fontWeight: 700, color: $T.accent, textTransform: "uppercase", marginBottom: 4 }}>{t.after}</div><div style={{ fontSize: 14, fontWeight: 700, color: $T.navy }}>{ex.after}</div></div></div>}
      {ex.type === "profile" && <div style={{ background: $T.bgSoft, borderRadius: 8, padding: 16 }}><div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: $T.navy, display: "flex", alignItems: "center", justifyContent: "center" }}><span style={{ color: $T.accent, fontWeight: 800, fontSize: 10 }}>BIO</span></div><div><div style={{ fontSize: 13, fontWeight: 700, color: $T.navy }}>Biomattone HC200</div><div style={{ fontSize: 11, color: $T.textSec }}>Verdecalce Srl</div></div><$Badge bg={$T.accentSoft} color={$T.accent} style={{ fontSize: 9, marginLeft: "auto" }}>82%</$Badge></div><div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>{["Dati tecnici", "Certificazioni", "Ambiente", "Documenti"].map((tab, j) => <span key={j} style={{ fontSize: 10, padding: "4px 10px", borderRadius: 6, background: j === 0 ? $T.navy : $T.white, color: j === 0 ? $T.accent : $T.textSec, fontWeight: 600, border: `1px solid ${j === 0 ? $T.navy : $T.border}` }}>{tab}</span>)}</div></div>}
      {ex.type === "spec" && <div style={{ background: $T.bgSoft, borderRadius: 8, padding: 16 }}><div style={{ fontSize: 10, fontWeight: 700, color: $T.textSec, textTransform: "uppercase", marginBottom: 8 }}>{ex.label}</div><div style={{ fontSize: 12, color: $T.textSec, lineHeight: 1.7, fontStyle: "italic" }}>{ex.quote}</div><div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 6 }}><$I d={$ic.check} size={14} color={$T.accent} /><span style={{ fontSize: 12, fontWeight: 600, color: $T.accent }}>{ex.ok}</span></div></div>}
      {ex.type === "update" && <div style={{ display: "flex", flexDirection: "column", gap: 6 }}><div style={{ background: $T.accentSoft, borderRadius: 8, padding: 10, display: "flex", alignItems: "center", gap: 8 }}><$I d={$ic.upload} size={16} color={$T.accent} /><span style={{ fontSize: 12, fontWeight: 600, color: $T.navy }}>{t.before === "Prima" ? "Certificazione aggiornata ✅" : "Certification updated ✅"}</span></div><div style={{ textAlign: "center" }}><$I d={$ic.chevDown} size={16} color={$T.accent} /></div>{ex.items.map((item, j) => <div key={j} style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 10px" }}><$I d={$ic.check} size={13} color={$T.accent} /><span style={{ fontSize: 12, color: $T.textDark }}>{item} {t.updated}</span></div>)}</div>}
      {ex.type === "trace" && <div style={{ borderRadius: 8, overflow: "hidden", border: `1px solid ${$T.border}` }}><div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", background: $T.navy }}>{ex.cols.map((h, j) => <div key={j} style={{ padding: "8px 10px", fontSize: 10, fontWeight: 700, color: $T.accent, textTransform: "uppercase" }}>{h}</div>)}</div>{ex.rows.map((r, j) => <div key={j} style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", background: j % 2 === 0 ? $T.white : $T.bgSoft }}><div style={{ padding: "8px 10px", fontSize: 11, color: $T.textDark, fontWeight: 600 }}>{r[0]}</div><div style={{ padding: "8px 10px", fontSize: 11, color: $T.textDark }}>{r[1]}</div><div style={{ padding: "8px 10px", fontSize: 11, color: $T.accent, fontWeight: 500 }}>📄 {r[2]}</div></div>)}</div>}
      {ex.type === "gaps" && <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>{ex.items.map(([label, ok], j) => <div key={j} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", borderRadius: 8, background: ok ? $T.accentSoft : $T.bgSoft }}>{ok ? <$I d={$ic.check} size={14} color={$T.accent} /> : <div style={{ width: 14, height: 14, borderRadius: "50%", border: `2px solid ${$T.textMuted}`, opacity: 0.4 }} />}<span style={{ fontSize: 12, color: ok ? $T.navy : $T.textSec, fontWeight: ok ? 600 : 400 }}>{label}</span>{!ok && <span style={{ fontSize: 10, color: $T.warn, fontWeight: 600, marginLeft: "auto" }}>{ex.miss}</span>}</div>)}</div>}
      <p style={S.cap}>{ex.caption}</p>
    </div>
  );
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MAIN LANDING
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function NewLandingPage({ onNavigate, L }) {
  const lang = L.lang; const setLang = L.setLang;
  const [formOpen, setFormOpen] = useState(false);
  const [formCtx, setFormCtx] = useState("hero");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [expandedFeat, setExpandedFeat] = useState(null);
  const [dppProd, setDppProd] = useState(null);
  const [dppTab, setDppTab] = useState(0);
  const t = $tx[lang];
  const font = "'DM Sans', 'Segoe UI', system-ui, sans-serif";

  $useScrollDepth();
  useEffect(() => { $track("page_viewed", { lang }); }, [lang]);
  useEffect(() => {
    const depths = [25, 50, 75, 100]; const fired = new Set();
    const onScroll = () => { const pct = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100); depths.forEach(d => { if (pct >= d && !fired.has(d)) { fired.add(d); $track("scroll_depth", { depth: d }); } }); };
    window.addEventListener("scroll", onScroll); return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const openForm = useCallback((ctx) => { $track("cta_clicked", { context: ctx, lang }); setFormCtx(ctx); setFormOpen(true); }, [lang]);
  const scrollTo = (id) => { document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }); setMobileMenu(false); };

  // Feature expansion: calculate which row a feature is in (3 per row)
  // (removed — features now open in modal)

  return (
    <div style={{ fontFamily: font, color: $T.textDark, background: $T.white, minHeight: "100vh", overflowX: "hidden" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;0,9..40,800&display=swap');
        *{margin:0;padding:0;box-sizing:border-box}html{scroll-behavior:smooth}
        ::selection{background:${$T.accentSoft};color:${$T.navy}}
        @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        .fu{animation:fadeUp .6s ease-out both}.fu1{animation-delay:.1s}.fu2{animation-delay:.2s}.fu3{animation-delay:.3s}
        @media(max-width:768px){.desk{display:none!important}.mob{display:flex!important}.fg{grid-template-columns:1fr!important}.hg{grid-template-columns:1fr!important}.sp{padding-left:20px!important;padding-right:20px!important}.h1m{font-size:30px!important}}
        @media(min-width:769px){.mob{display:none!important}}
      `}</style>

      {/* ─── NAV ─── */}
      <nav style={{ position: "sticky", top: 0, zIndex: 100, background: "rgba(255,255,255,0.92)", backdropFilter: "blur(12px)", borderBottom: `1px solid ${$T.borderLight}` }}>
        <div style={{ maxWidth: 1080, margin: "0 auto", padding: "0 24px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }} onClick={() => scrollTo("hero")}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}><img src={LOGO_SRC} alt="DeePPy" style={{ height: 36, width: 36, objectFit: "cover", borderRadius: 9 }} /><span style={{ fontWeight: 800, fontSize: 18, color: $T.navy }}>DeePPy</span></span>
          </div>
          <div className="desk" style={{ display: "flex", alignItems: "center", gap: 24 }}>
            {[["feat", t.nav.feat], ["how", t.nav.how], ["plans", t.nav.plans]].map(([id, l]) => <button key={id} onClick={() => scrollTo(id)} style={{ background: "none", border: "none", color: $T.textSec, fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: font }}>{l}</button>)}
            <button onClick={() => { $track("login_clicked"); onNavigate("login") }} style={{ background: "none", border: `1px solid ${$T.border}`, borderRadius: 8, padding: "7px 16px", color: $T.navy, fontSize: 13, fontWeight: 600, cursor: "pointer", fontFamily: font }}>{t.nav.login}</button>
            <div style={{ display: "flex", gap: 4 }}>{["it", "en"].map((l) => <button key={l} onClick={() => setLang(l)} style={{ background: lang === l ? $T.navy : "transparent", color: lang === l ? $T.white : $T.textSec, border: "none", borderRadius: 6, padding: "4px 10px", fontSize: 11, fontWeight: 700, cursor: "pointer", textTransform: "uppercase", fontFamily: font }}>{l}</button>)}</div>
            <$Btn primary onClick={() => openForm("nav")} style={{ padding: "8px 20px", fontSize: 13 }}>{t.nav.cta}</$Btn>
          </div>
          <div className="mob" style={{ display: "none", alignItems: "center", gap: 8 }}>
            <button onClick={() => { $track("login_clicked"); onNavigate("login"); }} style={{ background: "none", border: `1px solid ${$T.border}`, borderRadius: 7, padding: "5px 12px", color: $T.navy, fontSize: 12, fontWeight: 600, cursor: "pointer", fontFamily: font }}>{t.nav.login}</button>
            <div style={{ display: "flex", gap: 4 }}>{["it", "en"].map((l) => <button key={l} onClick={() => setLang(l)} style={{ background: lang === l ? $T.navy : "transparent", color: lang === l ? $T.white : $T.textSec, border: "none", borderRadius: 6, padding: "4px 8px", fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: font }}>{l}</button>)}</div>
            <button onClick={() => setMobileMenu(!mobileMenu)} style={{ background: "none", border: "none", cursor: "pointer" }}><$I d={mobileMenu ? $ic.x : $ic.menu} size={22} color={$T.navy} /></button>
          </div>
        </div>
        {mobileMenu && <div className="mob" style={{ display: "flex", flexDirection: "column", padding: "12px 24px 20px", gap: 12, borderTop: `1px solid ${$T.borderLight}`, background: $T.white }}>
          {[["feat", t.nav.feat], ["how", t.nav.how], ["plans", t.nav.plans]].map(([id, l]) => <button key={id} onClick={() => scrollTo(id)} style={{ background: "none", border: "none", color: $T.textDark, fontSize: 15, fontWeight: 600, cursor: "pointer", textAlign: "left", padding: "8px 0", fontFamily: font }}>{l}</button>)}
          <button onClick={() => { $track("login_clicked"); onNavigate("login"); setMobileMenu(false); }} style={{ background: "none", border: `1px solid ${$T.border}`, borderRadius: 8, padding: "10px 16px", color: $T.navy, fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: font, textAlign: "center" }}>{t.nav.login}</button>
          <$Btn primary onClick={() => { openForm("nav_mobile"); setMobileMenu(false); }} style={{ justifyContent: "center" }}>{t.nav.cta}</$Btn>
        </div>}
      </nav>

      {/* ─── HERO ─── */}
      <section id="hero" data-track-section className="sp" style={{ padding: "80px 24px 72px", textAlign: "center", maxWidth: 820, margin: "0 auto" }}>
        <div className="fu"><$Badge><$I d={$ic.shield} size={10} color={$T.accent} /> {t.hero.badge}</$Badge></div>
        <h1 className="fu fu1 h1m" style={{ fontSize: 44, fontWeight: 800, lineHeight: 1.12, margin: "20px 0 16px", color: $T.navy, whiteSpace: "pre-line", letterSpacing: "-0.03em" }}>{t.hero.h1}</h1>
        <p className="fu fu2" style={{ fontSize: 19, color: $T.textDark, lineHeight: 1.5, maxWidth: 600, margin: "0 auto 14px", fontWeight: 500 }}>{t.hero.sub}</p>
        <p className="fu fu2" style={{ fontSize: 15, color: $T.textSec, lineHeight: 1.65, maxWidth: 540, margin: "0 auto 36px" }}>{t.hero.body}</p>
        <div className="fu fu3" style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <$Btn primary onClick={() => openForm("hero_cta")} style={{ fontSize: 15, padding: "14px 32px" }}>{t.hero.cta1} <$I d={$ic.arrow} size={16} color={$T.navy} /></$Btn>
          <$Btn onClick={() => scrollTo("how")} style={{ fontSize: 15, padding: "14px 32px" }}>{t.hero.cta2}</$Btn>
        </div>
      </section>

      {/* ─── FEATURES (cards → click opens modal) ─── */}
      <section id="feat" data-track-section className="sp" style={{ padding: "72px 24px", background: $T.bg }}>
        <div style={{ maxWidth: 1020, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 40 }}><h2 style={{ fontSize: 30, fontWeight: 800, color: $T.navy }}>{t.feat.title}</h2></div>
          <div className="fg" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
            {t.feat.items.map((f, i) => (
              <button key={i} onClick={() => { setExpandedFeat(i); $track("feature_clicked", { feature: f.tag, index: i }); }}
                style={{ textAlign: "left", background: $T.white, border: `1px solid ${$T.border}`, borderRadius: 14, padding: 24, cursor: "pointer", fontFamily: font, transition: "all 0.2s", display: "flex", flexDirection: "column" }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = $T.accentBorder; e.currentTarget.style.boxShadow = `0 4px 20px rgba(46,196,160,0.08)`; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = $T.border; e.currentTarget.style.boxShadow = "none"; }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: $T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 14 }}><$I d={$ic[f.ic]} size={20} color={$T.accent} /></div>
                <$Badge bg={$T.bgSoft} color={$T.textSec} style={{ marginBottom: 10, fontSize: 10 }}>{f.tag}</$Badge>
                <h3 style={{ fontSize: 15, fontWeight: 700, color: $T.navy, lineHeight: 1.35, marginBottom: 8 }}>{f.h}</h3>
                <p style={{ fontSize: 13, color: $T.textSec, lineHeight: 1.6, flex: 1 }}>{f.p}</p>
                <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 4, color: $T.accent, fontSize: 12, fontWeight: 600 }}>
                  {t.seeEx} <$I d={$ic.arrow} size={14} color={$T.accent} />
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Feature example modal */}
      {expandedFeat !== null && (() => {
        const f = t.feat.items[expandedFeat];
        const ex = $featEx[lang][expandedFeat];
        return (
          <div style={{ position: "fixed", inset: 0, zIndex: 9999, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(11,29,58,0.6)", backdropFilter: "blur(4px)" }} onClick={() => setExpandedFeat(null)}>
            <div style={{ background: $T.white, borderRadius: 16, maxWidth: 480, width: "92%", maxHeight: "88vh", overflowY: "auto", position: "relative" }} onClick={(e) => e.stopPropagation()}>
              <div style={{ padding: "24px 28px 0", display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: $T.accentSoft, display: "flex", alignItems: "center", justifyContent: "center" }}><$I d={$ic[f.ic]} size={20} color={$T.accent} /></div>
                <div style={{ flex: 1 }}><$Badge bg={$T.bgSoft} color={$T.textSec} style={{ fontSize: 10 }}>{f.tag}</$Badge><h3 style={{ fontSize: 17, fontWeight: 800, color: $T.navy, marginTop: 4 }}>{f.h}</h3></div>
                <button onClick={() => setExpandedFeat(null)} style={{ background: "none", border: "none", cursor: "pointer", padding: 4 }}><$I d={$ic.x} size={18} color={$T.textSec} /></button>
              </div>
              <div style={{ padding: "16px 28px" }}><p style={{ fontSize: 13, color: $T.textSec, lineHeight: 1.6 }}>{f.p}</p></div>
              <div style={{ padding: "0 28px 24px" }}><$FeatPanel ex={ex} t={t} /></div>
            </div>
          </div>
        );
      })()}

      {/* ─── HOW IT WORKS ─── */}
      <section id="how" data-track-section className="sp" style={{ padding: "72px 24px" }}>
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 40 }}><h2 style={{ fontSize: 30, fontWeight: 800, color: $T.navy }}>{t.how.title}</h2></div>
          <div className="hg" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
            {t.how.steps.map((s, i) => (
              <div key={i}>
                <div style={{ fontSize: 48, fontWeight: 800, color: $T.accentSoft, letterSpacing: "-0.04em", marginBottom: 12 }}>{s.n}</div>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: $T.navy, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 16 }}><$I d={$ic[s.ic]} size={22} color={$T.accent} /></div>
                <h3 style={{ fontSize: 17, fontWeight: 700, color: $T.navy, lineHeight: 1.3, marginBottom: 10 }}>{s.h}</h3>
                <p style={{ fontSize: 13, color: $T.textSec, lineHeight: 1.65 }}>{s.p}</p>
                {s.p2 && (
                  <div style={{ marginTop: 12 }}>
                    <p style={{ fontSize: 13, color: $T.accent, lineHeight: 1.6, fontWeight: 500 }}>{s.p2}</p>
                    <button onClick={() => openForm("how_complete")} style={{ marginTop: 10, background: "none", border: `1px solid ${$T.accentBorder}`, borderRadius: 8, padding: "8px 18px", color: $T.accent, fontSize: 12, fontWeight: 600, cursor: "pointer", fontFamily: font, display: "inline-flex", alignItems: "center", gap: 6, transition: "all 0.2s" }}
                      onMouseEnter={(e) => { e.currentTarget.style.background = $T.accentSoft; }} onMouseLeave={(e) => { e.currentTarget.style.background = "none"; }}>
                      <$I d={$ic.puzzle} size={13} color={$T.accent} />{t.complete}
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CREDIBILITY ─── */}
      <section data-track-section id="cred" className="sp" style={{ padding: "48px 24px", background: $T.navy }}>
        <div style={{ maxWidth: 820, margin: "0 auto", display: "flex", gap: 20, justifyContent: "center", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 340px", padding: "20px 24px", borderRadius: 12, background: $T.navyMid, border: `1px solid ${$T.navyLight}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: $T.navyLight, display: "flex", alignItems: "center", justifyContent: "center" }}><$I d={$ic.award} size={16} color={$T.accent} /></div>
              <span style={{ fontSize: 14, fontWeight: 700, color: $T.text }}>{lang === "it" ? "Chi siamo" : "Who we are"}</span>
            </div>
            <p style={{ fontSize: 13, color: $T.textMuted, lineHeight: 1.6 }}>{t.cred.levery}</p>
          </div>
          <div style={{ flex: "1 1 340px", padding: "20px 24px", borderRadius: 12, background: $T.navyMid, border: `1px solid ${$T.navyLight}` }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: $T.navyLight, display: "flex", alignItems: "center", justifyContent: "center" }}><$I d={$ic.globe} size={16} color={$T.accent} /></div>
              <span style={{ fontSize: 14, fontWeight: 700, color: $T.text }}>{lang === "it" ? "Standard europeo" : "European standard"}</span>
            </div>
            <p style={{ fontSize: 13, color: $T.textMuted, lineHeight: 1.6 }}>{t.cred.reg}</p>
          </div>
        </div>
      </section>

      {/* ─── COMPETITIVE EDGE ─── */}
      <section id="edge" data-track-section className="sp" style={{ padding: "72px 24px", background: $T.bgSoft }}>
        <div style={{ maxWidth: 700, margin: "0 auto", textAlign: "center" }}>
          <$Badge bg={$T.navyLight} color={$T.accent}><$I d={$ic.globe} size={10} color={$T.accent} /> {t.edge.badge}</$Badge>
          <h2 style={{ fontSize: 26, fontWeight: 800, color: $T.navy, margin: "14px 0 14px", lineHeight: 1.3 }}>{t.edge.h}</h2>
          <p style={{ fontSize: 15, color: $T.textSec, lineHeight: 1.7 }}>{t.edge.p}</p>
        </div>
      </section>

      {/* ─── PLAN (simplified single block) ─── */}
      <section id="plans" data-track-section className="sp" style={{ padding: "72px 24px" }}>
        <div style={{ maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
          <h2 style={{ fontSize: 30, fontWeight: 800, color: $T.navy, marginBottom: 12 }}>{t.plan.h}</h2>
          <p style={{ fontSize: 15, color: $T.textSec, lineHeight: 1.7, marginBottom: 32 }}>{t.plan.sub}</p>
          <$Btn primary onClick={() => openForm("plan_starter")} style={{ fontSize: 16, padding: "15px 40px" }}>{t.plan.cta} <$I d={$ic.arrow} size={16} color={$T.navy} /></$Btn>
          <div style={{ marginTop: 24, padding: "16px 24px", borderRadius: 10, background: $T.bgSoft, border: `1px solid ${$T.border}`, display: "inline-flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 14, color: $T.textSec }}>{t.plan.more}</span>
            <button onClick={() => openForm("plan_multi")} style={{ background: "none", border: "none", color: $T.accent, fontWeight: 700, fontSize: 14, cursor: "pointer", fontFamily: font, textDecoration: "underline" }}>{t.plan.moreCta}</button>
          </div>
        </div>
      </section>

      {/* ─── CATALOG (3 distinct products) ─── */}
      <section id="catalog" data-track-section className="sp" style={{ padding: "72px 24px", background: $T.bgSoft }}>
        <div style={{ maxWidth: 760, margin: "0 auto", textAlign: "center" }}>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: $T.navy, marginBottom: 8 }}>{t.catalog.h}</h2>
          <p style={{ fontSize: 14, color: $T.textSec, lineHeight: 1.6, marginBottom: 28 }}>{t.catalog.sub}</p>
          <div style={{ display: "flex", gap: 14, justifyContent: "center", flexWrap: "wrap" }}>
            {$products[lang].map((prod) => (
              <button key={prod.id} onClick={() => { setDppProd(prod); setDppTab(0); $track("catalog_product_clicked", { product: prod.name }); }}
                style={{ padding: "16px 20px", borderRadius: 12, background: $T.white, border: `1px solid ${$T.border}`, display: "flex", alignItems: "center", gap: 12, cursor: "pointer", fontFamily: font, transition: "all 0.2s", textAlign: "left", minWidth: 220 }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = $T.accentBorder; e.currentTarget.style.boxShadow = `0 4px 16px rgba(46,196,160,0.08)`; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = $T.border; e.currentTarget.style.boxShadow = "none"; }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: $T.navy, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}><span style={{ color: $T.accent, fontWeight: 800, fontSize: 9 }}>{prod.name.split(" ")[0].slice(0, 4).toUpperCase()}</span></div>
                <div style={{ flex: 1 }}><div style={{ fontSize: 13, fontWeight: 700, color: $T.navy }}>{prod.name}</div><div style={{ fontSize: 11, color: $T.textSec }}>{prod.mfr}</div></div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <$Badge bg={$T.accentSoft} color={prod.pct >= 85 ? $T.accent : prod.pct >= 70 ? "#F5A623" : $T.warn} style={{ fontSize: 10, padding: "3px 10px" }}>{prod.pct}%</$Badge>
                </div>
              </button>
            ))}
          </div>
          <p style={{ fontSize: 12, color: $T.textSec, marginTop: 16, opacity: 0.7 }}>{t.catalog.note}</p>
        </div>
      </section>

      {/* ─── FINAL CTA ─── */}
      <section id="final" data-track-section className="sp" style={{ padding: "72px 24px", background: $T.navy, textAlign: "center" }}>
        <h2 style={{ fontSize: 30, fontWeight: 800, color: $T.text, lineHeight: 1.3, maxWidth: 600, margin: "0 auto 28px" }}>{t.final.h}</h2>
        <$Btn primary onClick={() => openForm("final_cta")} style={{ fontSize: 16, padding: "15px 40px" }}>{t.final.cta} <$I d={$ic.arrow} size={16} color={$T.navy} /></$Btn>
      </section>

      {/* ─── FOOTER (compact, with vision line) ─── */}
      <footer className="sp" style={{ padding: "32px 24px 28px", background: $T.navy, borderTop: `1px solid ${$T.navyMid}` }}>
        <div style={{ maxWidth: 1020, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <img src={LOGO_SRC} alt="DeePPy" style={{ height: 24, width: 24, objectFit: "cover", borderRadius: 6, opacity: 0.85 }} />
            <span style={{ fontSize: 14, fontWeight: 800, color: $T.text, opacity: 0.85 }}>DeePPy</span>
          </div>
          <p style={{ fontSize: 12, color: $T.textMuted, lineHeight: 1.9 }}>
            © 2026 DeePPy by <a href="https://www.levery.it/" target="_blank" rel="noopener noreferrer" style={{ color: $T.textMuted, textDecoration: "none" }}>Levery S.r.l. Società Benefit</a> — Via Pisino 66, 47814 Bellaria Igea Marina (RN), Italy<br />
            P.IVA 04730050400 — <a href="mailto:info@levery.it" style={{ color: $T.accent, textDecoration: "none" }}>info@levery.it</a> — <a href="#" style={{ color: $T.textMuted, textDecoration: "none" }}>Privacy</a> · <a href="#" style={{ color: $T.textMuted, textDecoration: "none" }}>{lang === "it" ? "Termini" : "Terms"}</a>
          </p>
          <p style={{ fontSize: 11, color: $T.textMuted, marginTop: 12, opacity: 0.5 }}>{t.footer.eu}</p>
        </div>
      </footer>

      {/* ─── MODALS ─── */}
      <$FormModal open={formOpen} onClose={() => setFormOpen(false)} t={t.form} context={formCtx} />
      {dppProd && <$DppModal lang={lang} prod={dppProd} activeTab={dppTab} onTab={(j) => { setDppTab(j); $track("dpp_tab_clicked", { tab: j, product: dppProd.name }); }} onClose={() => { setDppProd(null); $track("dpp_modal_closed"); }} onComplete={() => { setDppProd(null); openForm("dpp_complete_" + dppProd.name); }} onCta={() => { setDppProd(null); openForm("dpp_create_" + dppProd.name); }} t={t} />}
    </div>
  );
}



// ─── PUBLIC DPP VIEW (QR scan / public URL) ─────────────
function PublicDPPView({ onNavigate, L, isSpecific = false, dppData = null, imageUrl = null }) {
  const it = L?.lang === "it";
  const [tab, setTab] = useState("tech");
  const [expanded, setExpanded] = useState(0);
  const [hoverSupplier, setHoverSupplier] = useState(null);

  // Build the public product object from a real passport when available.
  const _pp = dppData?.passport;
  const _stats = dppData?.stats;
  const _ev = (path) => { const r = _ef(_pp, path); return r && r.v != null && r.v !== "" ? r.v : null; };
  const _gf = (obj, f) => { const x = obj?.[f]; return (x && typeof x === "object") ? x.value : x; };

  const realProduct = _pp ? {
    id: _ev("overview.product_info.uid") || "—",
    name: _ev("overview.product_info.product_name") || (it ? "Prodotto" : "Product"),
    manufacturer: {
      name: _ev("overview.manufacturer.company_name") || "—",
      location: _ev("overview.manufacturer.address") || _ev("overview.manufacturer.manufacturing_site") || "",
    },
    category: _ev("overview.product_info.product_family") || "",
    standard: _ev("compliance.dop_standard") || "",
    completion: Math.round(_stats?.completeness ?? 0),
    lastUpdated: "", version: "",
    technical: Object.fromEntries(
      (_pp.performance?.values || []).map(v => {
        const val = (v.value && typeof v.value === "object") ? v.value.value : v.value;
        return [v.property_name, `${val ?? ""}${v.unit ? " " + v.unit : ""}`.trim() || (it ? "Non dichiarato" : "Not declared")];
      })
    ),
    components: (_pp.composition?.materials || []).map(m => ({
      name: _gf(m, "description") || "—",
      pct: _gf(m, "percentage") ?? _gf(m, "quantity_per_product") ?? "",
      recycled: Number(_gf(m, "recycled_content")) || 0,
      origin: _gf(m, "origin") || "",
    })),
    env: {
      gwp: (() => {
        const stages = _pp.lifecycle?.stages || [];
        const a13 = stages.find(s => (s.stage_code || "").replace(/[\s-]/g, "").toUpperCase().includes("A1A3")) || stages[0];
        const g = a13 ? _gf(a13, "gwp_total") : null;
        return { value: g != null ? String(g) : "—", unit: "kg CO₂ eq", phase: a13?.stage_code || "A1-A3" };
      })(),
      recycled: { value: "—", detail: it ? "Da EPD" : "From EPD" },
      recyclability: { value: "—", detail: "" },
      epd: { number: (_pp.compliance?.product_certifications || []).find(c => (_gf(c, "name") || "").toUpperCase().includes("EPD")) ? _gf((_pp.compliance.product_certifications.find(c => (_gf(c, "name") || "").toUpperCase().includes("EPD"))), "reference_number") || "—" : "—", valid: "" },
      energyLabel: "—",
    },
    certs: (_pp.compliance?.product_certifications || []).map(c => ({
      name: _gf(c, "name") || "—",
      num: _gf(c, "reference_number") || "",
      valid: _gf(c, "valid_until") || "",
      issuer: _gf(c, "issuing_body") || "",
    })),
    // Show every uploaded source file. The DB-backed `dppData.documents` list
    // is authoritative — it includes everything the user actually uploaded
    // (PDFs, BoM xlsx, images). The passport's `_pp.documents` section only
    // carries files that postprocess could slot into specific buckets (it
    // drops DoP/DoC/EPD/BoM, so most uploads silently disappeared from this
    // tab). Fall back to that section, then to metadata.source_documents,
    // only when no DB list is available (e.g. legacy or demo data).
    docs: (() => {
      const fromDb = (dppData?.documents || []).map(d => ({
        id: d.id,
        name: d.filename || "—",
        type: (d.doc_type || (d.filename || "").split(".").pop() || "").toUpperCase() || "PDF",
        size: d.size_bytes ? `${(d.size_bytes / 1048576).toFixed(1)} MB` : "",
        date: "",
      }));
      if (fromDb.length) return fromDb;
      const fromSlots = Object.entries(_pp.documents || {}).flatMap(([cat, list]) =>
        (Array.isArray(list) ? list : []).map(d => ({
          name: d.filename || cat,
          type: (d.filename || "").split(".").pop()?.toUpperCase() || "PDF",
          size: "", date: "",
        }))
      );
      if (fromSlots.length) return fromSlots;
      return (_pp.metadata?.source_documents || []).map(fn => ({
        name: fn,
        type: (fn || "").split(".").pop()?.toUpperCase() || "PDF",
        size: "", date: "",
      }));
    })(),
    versions: [],
    project: isSpecific ? { batch: "", site: "", ref: "", dims: "", weight: "", date: "" } : null,
  } : null;

  const demoProduct = {
    id: "DPP-20260115-a3f8", name: "Pannello Isolante XPS 100mm",
    manufacturer: { name: "Ediltech S.r.l.", location: "Modena, Italia" },
    category: it ? "Isolanti Termici" : "Thermal Insulation",
    standard: "EN 13164:2012+A2:2023", completion: 94,
    lastUpdated: "2 Mar 2026, 10:42", version: "v2.3",
    technical: {
      [it?"Conduttivit\u00e0 termica \u03bb":"Thermal conductivity \u03bb"]: "0.034 W/(m\u00b7K)",
      [it?"Resistenza termica R":"Thermal resistance R"]: "2.94 m\u00b2\u00b7K/W",
      [it?"Resistenza a compressione":"Compressive strength"]: "\u2265 300 kPa",
      [it?"Assorbimento acqua":"Water absorption"]: "\u2264 0.7 vol.%",
      [it?"Classe reazione al fuoco":"Fire reaction class"]: "E (Euroclass)",
      [it?"Densit\u00e0":"Density"]: "32 \u00b1 2 kg/m\u00b3",
      [it?"Spessore nominale":"Nominal thickness"]: "100 mm",
      [it?"Dimensioni pannello":"Panel dimensions"]: "1250 \u00d7 600 mm",
      [it?"Stabilit\u00e0 dimensionale":"Dimensional stability"]: "\u2264 2% (70\u00b0C, 48h)",
      [it?"Temperatura di esercizio":"Operating temperature"]: "-50\u00b0C / +75\u00b0C",
      "GTIN/EAN": it?"Non dichiarato":"Not declared",
      [it?"Lotto di produzione":"Production batch"]: it?"Non dichiarato":"Not declared",
    },
    components: [
      { name: "Polistirene espanso estruso (XPS)", pct: 94.5, recycled: 12, origin: "UE" },
      { name: it?"Agente espandente (CO\u2082)":"Blowing agent (CO\u2082)", pct: 3.2, recycled: 0, origin: "UE" },
      { name: it?"Additivi ritardanti di fiamma":"Flame retardant additives", pct: 1.8, recycled: 0, origin: "UE" },
      { name: it?"Colorante (pigmento blu)":"Colorant (blue pigment)", pct: 0.5, recycled: 0, origin: "UE" },
    ],
    env: { gwp: { value: "3.4", unit: "kg CO\u2082 eq/m\u00b2", phase: "A1-A3" }, recycled: { value: "12%", detail: "Post-consumer" }, recyclability: { value: "100%", detail: it?"Meccanico":"Mechanical" }, epd: { number: "EPD-EDT-2024-0847", valid: "2024-2029" }, energyLabel: "A+" },
    certs: [
      { name: it?"Marcatura CE":"CE Marking", num: "CE-0432-CPR-2024", valid: "2024-2029", issuer: "T\u00dcV S\u00dcD" },
      { name: "EPD", num: "EPD-EDT-2024-0847", valid: "2024-2029", issuer: "EPDItaly" },
      { name: it?"CAM Conformit\u00e0":"CAM Compliance", num: "DM 23/06/2022", valid: it?"In vigore":"Active", issuer: "Min. Ambiente" },
      { name: "DoP", num: "DoP-XPS100-2024-R3", valid: "2024", issuer: "Ediltech" },
    ],
    docs: [
      { name: it?"Scheda Tecnica":"Technical Datasheet", type: "PDF", size: "2.4 MB", date: "Gen 2026" },
      { name: "DoP", type: "PDF", size: "1.8 MB", date: "Gen 2026" },
      { name: "EPD", type: "PDF", size: "3.1 MB", date: "Nov 2024" },
      { name: it?"Certificato CE":"CE Certificate", type: "PDF", size: "890 KB", date: "Feb 2024" },
      { name: it?"Rapporto di prova":"Test Report", type: "PDF", size: "1.2 MB", date: "Dic 2023" },
      { name: "SDS", type: "PDF", size: "540 KB", date: "Set 2024" },
    ],
    versions: [
      { ver: "v2.3", date: "2 Mar 2026", author: "Sistema", changes: [
        { type: "updated", field: "Resistenza termica R", from: "2.85", to: "2.94 m\u00b2\u00b7K/W", section: it?"Dati Tecnici":"Technical" },
        { type: "added", field: "EPD", detail: "EPD-EDT-2024-0847", section: it?"Documenti":"Documents" },
      ]},
      { ver: "v2.2", date: "18 Feb 2026", author: "M. Rossi", changes: [
        { type: "updated", field: it?"Contenuto riciclato":"Recycled content", from: "8%", to: "12%", section: it?"Ambiente":"Environment" },
        { type: "updated", field: "GWP (A1-A3)", from: "3.8", to: "3.4 kg CO\u2082 eq/m\u00b2", section: it?"Ambiente":"Environment" },
        { type: "added", field: "CAM", detail: it?"Certificazione aggiunta":"Certification added", section: it?"Certificazioni":"Certifications" },
      ]},
      { ver: "v2.1", date: "5 Feb 2026", author: "M. Rossi", changes: [
        { type: "updated", field: it?"Densit\u00e0":"Density", from: "30 \u00b1 2", to: "32 \u00b1 2 kg/m\u00b3", section: it?"Dati Tecnici":"Technical" },
        { type: "removed", field: it?"Cert. provvisorio":"Temp. certificate", detail: it?"Sostituito da CE definitivo":"Replaced by final CE", section: it?"Documenti":"Documents" },
      ]},
      { ver: "v2.0", date: "20 Gen 2026", author: "Sistema", changes: [
        { type: "added", field: "CE", detail: "CE-0432-CPR-2024", section: it?"Certificazioni":"Certifications" },
        { type: "added", field: "DoP", detail: it?"Caricata":"Uploaded", section: it?"Documenti":"Documents" },
        { type: "updated", field: it?"Completezza":"Completeness", from: "67%", to: "87%", section: it?"Generale":"General" },
      ]},
      { ver: "v1.0", date: "15 Gen 2026", author: "Sistema", changes: [
        { type: "created", field: "DPP", detail: it?"Estrazione automatica":"Auto-extraction", section: it?"Generale":"General" },
        { type: "added", field: it?"10 campi tecnici":"10 technical fields", detail: it?"Conduttivit\u00e0, resistenza, densit\u00e0\u2026":"Conductivity, resistance, density\u2026", section: it?"Dati Tecnici":"Technical" },
      ]},
    ],
    project: isSpecific ? {
      batch: "PR-2026-047",
      site: it?"Stabilimento Treviso":"Treviso plant",
      ref: it?"Commessa Villa Marchetti":"Order Villa Marchetti",
      dims: "1200\u00d71500mm",
      weight: "38 kg",
      date: "18 Mar 2026",
    } : null,
  };

  const p = realProduct || demoProduct;
  const mono = "'JetBrains Mono','SF Mono',monospace";

  // Completion ring
  const Ring = ({ value, sz = 48 }) => {
    const r = (sz - 6) / 2, circ = 2 * Math.PI * r, off = circ - (value / 100) * circ;
    const col = value >= 90 ? T.accent : value >= 60 ? T.amber : T.red;
    return (<svg width={sz} height={sz} style={{ transform: "rotate(-90deg)" }}><circle cx={sz/2} cy={sz/2} r={r} fill="none" stroke={T.border} strokeWidth="3" /><circle cx={sz/2} cy={sz/2} r={r} fill="none" stroke={col} strokeWidth="3" strokeDasharray={circ} strokeDashoffset={off} strokeLinecap="round" /><text x={sz/2} y={sz/2} textAnchor="middle" dominantBaseline="central" style={{ transform: "rotate(90deg)", transformOrigin: "center", fontSize: sz*0.28, fontWeight: 700, fill: "#F1F5F9", fontFamily: font }}>{value}%</text></svg>);
  };

  const Row = ({ label, value }) => (<div style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: `1px solid ${T.borderLight}` }}><span style={{ fontSize: 13, color: T.textSec }}>{label}</span><span style={{ fontSize: 13, fontWeight: 600, color: T.textDark, fontFamily: mono }}>{value}</span></div>);

  const chSt = { created: { color: T.accent, bg: T.accentSoft, d: ic.plus }, added: { color: T.accentDark||T.accent, bg: T.accentSoft, d: ic.plus }, updated: { color: "#3B82F6", bg: "#EFF6FF", d: ic.edit }, removed: { color: T.red, bg: T.redSoft||"#FEE2E2", d: ic.close } };

  // Product Image (same icon style as catalog cards)
  const ProductImg = () => (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "28px 20px", background: `linear-gradient(135deg, ${T.bgSoft}, ${T.accentSoft}40)` }}>
      {imageUrl
        ? <img src={imageUrl} alt={p.name} style={{ width: 90, height: 90, borderRadius: 16, objectFit: "cover", border: `1px solid ${T.borderLight}`, background: T.bgSoft }} />
        : <div style={{ width: 90, height: 90, borderRadius: 16, background: `linear-gradient(135deg, ${T.bgSoft}, ${T.accentSoft}60)`, display: "flex", alignItems: "center", justifyContent: "center", border: `1px solid ${T.borderLight}` }}><I d={ic.box} size={40} color={T.accent} /></div>
      }
    </div>);

  // Tab panels
  const PanelTech = () => (<div><div style={{ marginBottom: 14 }}><Badge color={T.textSec} bg={T.borderLight}>{it?"Norma":"Standard"}: {p.standard}</Badge></div>{Object.entries(p.technical).map(([k,v])=><Row key={k} label={k} value={v} />)}</div>);

  const PanelComp = () => {
    const bomNodes = [
      { id: "xps", name: "Polistirene espanso estruso (XPS)", pct: 94.5, recycled: 12, supplier: "Levery srl", supplierIdx: 0, children: [
        { id: "xps-v", name: it?"Granuli XPS vergini":"Virgin XPS granules", pct: 82.5, origin: "UE", supplier: "Levery srl", supplierIdx: 0 },
        { id: "xps-r", name: it?"Granuli XPS riciclati":"Recycled XPS granules", pct: 12, origin: "UE", supplier: "Rockwool Italia", supplierIdx: 2, recycled: true },
      ]},
      { id: "co2", name: it?"Agente espandente (CO\u2082)":"Blowing agent (CO\u2082)", pct: 3.2, origin: "UE", supplier: "Metra SpA", supplierIdx: 3 },
      { id: "flame", name: it?"Ritardanti di fiamma":"Flame retardants", pct: 1.8, origin: "UE/DE", supplier: "BASF SE", supplierIdx: 4, children: [
        { id: "flame-p", name: it?"Ritardante polimerico":"Polymeric retardant", pct: 1.5, origin: "DE", supplier: "BASF SE", supplierIdx: 4 },
        { id: "flame-s", name: it?"Sinergizzante":"Synergist", pct: 0.3, origin: "UE", supplier: "Arpa Industriale", supplierIdx: 1 },
      ]},
      { id: "color", name: it?"Colorante (pigmento blu)":"Colorant (blue pigment)", pct: 0.5, origin: "UE", supplier: "Arpa Industriale", supplierIdx: 1 },
    ];
    const toX = lng => ((lng + 12) / 36) * 360 + 20;
    const toY = lat => ((58 - lat) / 22) * 210 + 5;
    const TreeNode = ({ node, depth = 0 }) => {
      const hl = hoverSupplier === node.supplierIdx;
      const hasKids = node.children && node.children.length > 0;
      return (<div>
        <div onMouseEnter={() => setHoverSupplier(node.supplierIdx)} onMouseLeave={() => setHoverSupplier(null)} style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 10px", marginLeft: depth * 18, borderRadius: 7, background: hl ? T.accentSoft+"60" : node.recycled ? T.accentSoft+"30" : T.bg, border: `1px solid ${hl ? T.accent : T.borderLight}`, marginBottom: 3, cursor: "default", transition: "all 0.15s" }}>
          <div style={{ width: 22, height: 22, borderRadius: 5, background: depth === 0 ? T.accentSoft : T.bgSoft, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
            <I d={depth === 0 ? ic.layers : ic.droplet} size={10} color={depth === 0 ? (T.accentDark||T.accent) : T.textSec} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: T.textDark, lineHeight: 1.2 }}>{node.name}</div>
            <div style={{ display: "flex", gap: 6, fontSize: 9, color: T.textSec, marginTop: 1, flexWrap: "wrap", alignItems: "center" }}>
              {node.supplier && <span style={{ display: "inline-flex", alignItems: "center", gap: 2 }}><I d={ic.factory} size={8} color={T.textSec} />{node.supplier}</span>}
              {node.origin && <span>{node.origin}</span>}
              {node.recycled && <Badge color={T.accentDark||T.accent} bg={T.accentSoft} style={{ fontSize: 8, padding: "0 4px" }}>{"♻"}</Badge>}
            </div>
          </div>
          <span style={{ fontSize: 12, fontWeight: 700, color: T.navy, fontFamily: mono, flexShrink: 0 }}>{node.pct}%</span>
        </div>
        {hasKids && <div style={{ marginLeft: depth * 18 + 10, borderLeft: `1.5px solid ${T.border}`, paddingLeft: 6 }}>
          {node.children.map((ch, ci) => <TreeNode key={ci} node={ch} depth={depth + 1} />)}
        </div>}
      </div>);
    };
    return (<div>
      <div style={{ display: "flex", flexWrap: "wrap", borderRadius: 10, border: `1px solid ${T.border}`, overflow: "hidden", marginBottom: 10 }}>
        {/* Map - left (stacks on top on mobile) */}
        <div style={{ minWidth: 220, width: "35%", flexShrink: 0, flexGrow: 0, padding: 10, background: T.bgSoft, borderRight: `1px solid ${T.borderLight}` }}>
          <svg viewBox="0 0 400 220" style={{ width: "100%", display: "block", minHeight: 170 }}>
            <path d="M80,20 L100,15 L130,12 L165,10 L200,8 L240,10 L275,15 L310,12 L340,18 L360,30 L370,50 L375,75 L372,100 L365,125 L350,148 L330,165 L305,175 L275,182 L240,185 L205,183 L175,178 L145,170 L120,158 L100,142 L85,122 L75,98 L72,72 L75,48 L78,32 Z" fill={T.bg} stroke={T.border} strokeWidth={1.5} />
            <path d="M210,95 L220,110 L225,130 L218,150 L210,165 L205,155 L208,135 L205,115 L210,95" fill={T.accentSoft+"60"} stroke={T.accent} strokeWidth={0.8} />
            {supplyPoints.filter(sp => sp.type === "supplier").map((sp, si) => (
              <line key={si} x1={toX(supplyPoints[0].lng)} y1={toY(supplyPoints[0].lat)} x2={toX(sp.lng)} y2={toY(sp.lat)} stroke={hoverSupplier === si + 1 ? T.accent : T.border} strokeWidth={hoverSupplier === si + 1 ? 2.5 : 1} strokeDasharray={hoverSupplier === si + 1 ? "0" : "4,3"} opacity={hoverSupplier === si + 1 ? 1 : 0.3} style={{ transition: "all 0.2s" }} />
            ))}
            {supplyPoints.map((sp, si) => {
              const hl = hoverSupplier === si;
              return (<g key={si} onMouseEnter={() => setHoverSupplier(si)} onMouseLeave={() => setHoverSupplier(null)} style={{ cursor: "pointer" }}>
                {hl && <circle cx={toX(sp.lng)} cy={toY(sp.lat)} r={14} fill={T.accent} opacity={0.15} />}
                <circle cx={toX(sp.lng)} cy={toY(sp.lat)} r={hl ? 7 : 5} fill={sp.type === "producer" ? T.accent : hl ? T.accent : T.navy} stroke={T.bg} strokeWidth={2} style={{ transition: "all 0.15s" }} />
                {hl && <g>
                  <rect x={toX(sp.lng) - 55} y={toY(sp.lat) - 28} width={110} height={20} rx={4} fill={T.navy} opacity={0.92} />
                  <text x={toX(sp.lng)} y={toY(sp.lat) - 15} textAnchor="middle" fontSize={8} fill="#F1F5F9" fontFamily={font} fontWeight="600">{sp.name.length > 18 ? sp.name.slice(0, 18) + "…" : sp.name}</text>
                </g>}
                {!hl && <text x={toX(sp.lng)} y={toY(sp.lat) + 14} textAnchor="middle" fontSize={7} fill={T.textSec} fontFamily={font}>{sp.city.split(",")[0]}</text>}
              </g>);
            })}
          </svg>
        </div>
        {/* BOM tree - right (goes below map on mobile) */}
        <div style={{ flex: 1, minWidth: 280, padding: 12, overflowY: "auto", maxHeight: 400 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 10px", borderRadius: 7, background: T.navy+"12", border: `1px solid ${T.navy+"30"}`, marginBottom: 6 }}>
            <div style={{ width: 26, height: 26, borderRadius: 6, background: T.accent+"30", display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.box} size={12} color={T.accent} /></div>
            <div style={{ flex: 1 }}><div style={{ fontSize: 12, fontWeight: 700, color: T.navy }}>{p.name}</div><div style={{ fontSize: 9, color: T.textSec }}>{p.manufacturer.name} {"·"} {p.manufacturer.location}</div></div>
          </div>
          {bomNodes.map((node, ni) => <TreeNode key={ni} node={node} />)}
        </div>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        {[[it?"Fornitori UE":"EU Suppliers","100%",T.accent],[it?"Paesi":"Countries","2 (IT, DE)",T.textDark],[it?"Entro 500km":"Within 500km","75%",T.accent]].map(([l,v,c],i)=>(<div key={i} style={{ flex: 1, padding: "8px 10px", borderRadius: 7, border: `1px solid ${T.borderLight}`, background: T.bg, textAlign: "center" }}><div style={{ fontSize: 9, color: T.textSec, textTransform: "uppercase", fontWeight: 600 }}>{l}</div><div style={{ fontSize: 15, fontWeight: 800, color: c }}>{v}</div></div>))}
      </div>
      <div style={{ marginTop: 8, padding: "8px 10px", borderRadius: 6, background: T.accentSoft+"40", border: `1px solid ${T.accent}30`, fontSize: 10, color: T.textSec, display: "flex", alignItems: "center", gap: 6 }}><I d={ic.shield} size={12} color={T.accentDark||T.accent} />{it?"BOM + tracciabilità conforme ESPR Art. 9":"BOM + traceability compliant with ESPR Art. 9"}</div>
    </div>);
  };

  const PanelProject = () => p.project ? (<div>
    <div style={{ padding: "14px 16px", borderRadius: 10, background: T.accentSoft+"40", border: `1px solid ${T.accent}30`, marginBottom: 14, display: "flex", alignItems: "center", gap: 10 }}>
      <I d={ic.clip} size={16} color={T.accentDark||T.accent} />
      <div><div style={{ fontSize: 13, fontWeight: 700, color: T.accentDark||T.accent }}>{it?"DPP Progetto":"Project DPP"}</div><div style={{ fontSize: 11, color: T.textSec }}>{it?"Informazioni di progetto/commessa":"Project/order information"}</div></div>
    </div>
    <Row label={it?"Lotto di produzione":"Production batch"} value={p.project.batch} />
    <Row label={it?"Stabilimento produttivo":"Production site"} value={p.project.site} />
    <Row label={it?"Commessa / Cliente":"Order / Client"} value={p.project.ref} />
    <Row label={it?"Dimensioni reali":"Actual dimensions"} value={p.project.dims} />
    <Row label={it?"Peso reale":"Actual weight"} value={p.project.weight} />
    <Row label={it?"Data produzione":"Production date"} value={p.project.date} />
    <div style={{ marginTop: 14, padding: "10px 14px", borderRadius: 8, background: T.bgSoft, border: `1px solid ${T.borderLight}`, fontSize: 11, color: T.textSec, display: "flex", alignItems: "center", gap: 6 }}><I d={ic.link} size={12} color={T.accent} />{it?"Le informazioni generali del prodotto sono ereditate dal DPP Generale":"General product information is inherited from the General DPP"}</div>
  </div>) : null;

  const PanelEnv = () => { const e = p.env; return (<div><div style={{ display: "flex", alignItems: "center", gap: 16, padding: 20, borderRadius: 12, background: `${T.accentSoft}60`, border: `1px solid ${T.accent}30`, marginBottom: 20 }}><div style={{ width: 56, height: 56, borderRadius: 12, background: T.accent, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, fontWeight: 800, color: T.navy }}>{e.energyLabel}</div><div><div style={{ fontSize: 14, fontWeight: 700, color: T.textDark }}>{it?"Classe Energetica":"Energy Class"}</div><div style={{ fontSize: 12, color: T.textSec }}>{it?"Efficienza isolamento":"Insulation efficiency"}</div></div></div><div style={{ padding: 16, borderRadius: 10, border: `1px solid ${T.border}`, marginBottom: 12, background: T.bg }}><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 6 }}>GWP ({e.gwp.phase})</div><div style={{ fontSize: 28, fontWeight: 800, color: T.navy, fontFamily: mono }}>{e.gwp.value} <span style={{ fontSize: 13, fontWeight: 500, color: T.textSec }}>{e.gwp.unit}</span></div></div><div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>{[[it?"Contenuto Riciclato":"Recycled Content",e.recycled.value,e.recycled.detail],[it?"Riciclabilità":"Recyclability",e.recyclability.value,e.recyclability.detail]].map(([t,v,d],i)=>(<div key={i} style={{ padding: 16, borderRadius: 10, border: `1px solid ${T.border}` }}><div style={{ fontSize: 11, fontWeight: 600, color: T.textSec, textTransform: "uppercase", marginBottom: 4 }}>{t}</div><div style={{ fontSize: 22, fontWeight: 800, color: T.accentDark||T.accent }}>{v}</div><div style={{ fontSize: 11, color: T.textSec }}>{d}</div></div>))}</div><div style={{ marginTop: 12, padding: 12, borderRadius: 8, background: T.bgSoft, border: `1px solid ${T.borderLight}` }}><div style={{ fontSize: 11, color: T.textSec }}>EPD N° <strong style={{ color: T.textDark }}>{e.epd.number}</strong> — {e.epd.valid}</div></div></div>); };

  const PanelDocs = () => (<div>{p.docs.map((d,i)=>(<div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderRadius: 10, border: `1px solid ${T.border}`, marginBottom: 8, background: T.bg, cursor: "pointer" }}><div style={{ display: "flex", alignItems: "center", gap: 12 }}><div style={{ width: 36, height: 36, borderRadius: 8, background: `${T.red}12`, display: "flex", alignItems: "center", justifyContent: "center" }}><I d={ic.file} size={16} color={T.red} /></div><div><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{d.name}</div><div style={{ fontSize: 11, color: T.textSec }}>{d.type} {"·"} {d.size} {"·"} {d.date}</div></div></div><I d={ic.download} size={16} color={T.accent} /></div>))}</div>);

  const PanelHistory = () => (<div><p style={{ fontSize: 12, color: T.textSec, marginBottom: 16 }}>{it?"Cronologia completa delle modifiche":"Complete changelog"}</p>{p.versions.map((v,vi)=>{const isOpen=expanded===vi;const isFirst=vi===p.versions.length-1;const isLast=vi===0;return(<div key={vi} style={{ position: "relative", paddingLeft: 28 }}>{vi<p.versions.length-1&&<div style={{ position: "absolute", left: 9, top: 24, bottom: -2, width: 2, background: isOpen ? T.accent : T.border }} />}<div style={{ position: "absolute", left: 3, top: 6, width: 14, height: 14, borderRadius: "50%", background: isLast ? T.accent : isFirst ? T.navy : T.bg, border: `2.5px solid ${isLast ? T.accent : isFirst ? T.navy : T.border}`, zIndex: 2, boxShadow: isLast ? `0 0 0 3px ${T.accentSoft}` : "none" }} /><div onClick={()=>setExpanded(isOpen?-1:vi)} style={{ padding: "12px 16px", borderRadius: 10, marginBottom: 10, cursor: "pointer", border: `1px solid ${isOpen ? T.accent+"50" : T.border}`, background: isOpen ? T.accentSoft+"30" : T.bg }}><div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><div style={{ display: "flex", alignItems: "center", gap: 8 }}><span style={{ fontSize: 13, fontWeight: 700, color: T.navy, fontFamily: mono }}>{v.ver}</span>{isLast&&<Badge color={T.accentDark||T.accent} bg={T.accentSoft}>{it?"ATTUALE":"CURRENT"}</Badge>}{isFirst&&<Badge color={T.textSec} bg={T.borderLight}>{it?"PRIMA RELEASE":"FIRST RELEASE"}</Badge>}</div><span style={{ fontSize: 11, color: T.textSec }}>{v.date}</span></div><div style={{ display: "flex", gap: 4, marginTop: 6, flexWrap: "wrap" }}>{v.changes.map((ch,ci)=>{const st=chSt[ch.type]||chSt.added;return(<span key={ci} style={{ display: "inline-flex", alignItems: "center", gap: 3, padding: "2px 7px", borderRadius: 4, fontSize: 10, fontWeight: 600, color: st.color, background: st.bg }}><I d={st.d} size={9} color={st.color} />{ch.field.length>20?ch.field.slice(0,20)+"\u2026":ch.field}</span>);})}</div>{isOpen&&<div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${T.border}` }}><div style={{ fontSize: 11, color: T.textSec, marginBottom: 10 }}>{it?"Autore":"Author"}: <strong style={{ color: T.textDark }}>{v.author}</strong></div>{v.changes.map((ch,ci)=>{const st=chSt[ch.type]||chSt.added;return(<div key={ci} style={{ padding: "10px 12px", borderRadius: 8, marginBottom: 6, background: T.bg, border: `1px solid ${T.borderLight}` }}><div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}><div style={{ width: 20, height: 20, borderRadius: 5, display: "flex", alignItems: "center", justifyContent: "center", background: st.bg }}><I d={st.d} size={10} color={st.color} /></div><span style={{ fontSize: 12, fontWeight: 600, color: T.textDark }}>{ch.field}</span><Badge color={T.textSec} bg={T.borderLight}>{ch.section}</Badge></div>{ch.from&&ch.to?(<div style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: 26, fontSize: 12, flexWrap: "wrap" }}><span style={{ padding: "2px 8px", borderRadius: 4, background: T.redSoft||"#FEE2E2", color: T.red, textDecoration: "line-through", fontFamily: mono, fontSize: 11 }}>{ch.from}</span><span style={{ color: T.textSec, fontSize: 10 }}>{"→"}</span><span style={{ padding: "2px 8px", borderRadius: 4, background: T.accentSoft, color: T.accentDark||T.accent, fontWeight: 600, fontFamily: mono, fontSize: 11 }}>{ch.to}</span></div>):ch.detail?(<div style={{ marginLeft: 26, fontSize: 12, color: T.textSec }}>{ch.detail}</div>):null}</div>);})}</div>}</div></div>);})}</div>);

  const baseTabs = [
    { id: "tech", label: it?"Dati Tecnici":"Technical", d: ic.sliders },
    { id: "comp", label: it?"Componenti":"Components", d: ic.layers },
    ...(isSpecific ? [{ id: "project", label: it?"Progetto":"Project", d: ic.clip }] : []),
    { id: "env", label: it?"Ambiente":"Environment", d: ic.leaf },
    { id: "docs", label: it?"Documenti":"Documents", d: ic.file },
    { id: "history", label: it?"Versioni":"Versions", d: ic.clock },
  ];
  const tabs = baseTabs;

  const ActivePanel = { tech: PanelTech, comp: PanelComp, project: PanelProject, env: PanelEnv, docs: PanelDocs, history: PanelHistory }[tab];

  return (
    <div style={{ fontFamily: font, background: T.bgSoft, minHeight: "100vh" }}>
      {/* Header: manufacturer */}
      <div style={{ background: T.navy, borderBottom: `3px solid ${T.accent}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 20px", borderBottom: `1px solid ${T.navyLight}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}><I d={ic.shield} size={14} color={T.accent} /><span style={{ fontSize: 10.5, fontWeight: 700, color: T.accent, letterSpacing: "0.08em", textTransform: "uppercase" }}>{it?"Passaporto Digitale Verificato":"Verified Digital Passport"}</span></div>
          <span style={{ fontSize: 10, color: T.textSec, fontFamily: mono }}>{p.id}</span>
        </div>
        <div style={{ padding: "18px 20px 22px", display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 50, height: 50, borderRadius: 12, background: T.navyLight, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, fontWeight: 800, color: T.accent, flexShrink: 0 }}>E</div>
          <div style={{ flex: 1 }}><div style={{ fontSize: 17, fontWeight: 700, color: "#F1F5F9" }}>{p.manufacturer.name}</div><div style={{ fontSize: 12, color: T.textSec, marginTop: 1 }}>{p.manufacturer.location}</div></div>
          <Ring value={p.completion} sz={48} />
        </div>
      </div>

      {/* Product image */}
      <div style={{ background: T.bg, borderBottom: `1px solid ${T.border}` }}>
        <ProductImg />
        <div style={{ padding: "18px 20px 16px" }}>
          <Badge color={T.accentDark||T.accent} bg={T.accentSoft}>{p.category}</Badge>
          <h1 style={{ fontSize: 21, fontWeight: 800, color: T.navy, margin: "8px 0 0", lineHeight: 1.2 }}>{p.name}</h1>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8, fontSize: 11, color: T.textSec, flexWrap: "wrap" }}>
            <span><I d={ic.clock} size={11} /> {p.lastUpdated}</span>
            <span style={{ opacity: 0.4 }}>{"·"}</span>
            <span>{p.version}</span>
            <span style={{ opacity: 0.4 }}>{"·"}</span>
            <span style={{ color: T.accent, fontWeight: 600, cursor: "pointer" }} onClick={()=>setTab("history")}>{p.versions.length} {it?"versioni":"versions"}</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ background: T.bg, position: "sticky", top: 0, zIndex: 10, borderBottom: `1px solid ${T.border}` }}>
        <div style={{ display: "flex", overflowX: "auto", padding: "0 12px" }}>
          {tabs.map(t => { const on = tab === t.id; return (
            <button key={t.id} onClick={()=>setTab(t.id)} style={{ display: "flex", alignItems: "center", gap: 5, padding: "13px 12px", background: "none", border: "none", borderBottom: `2.5px solid ${on ? T.accent : "transparent"}`, color: on ? T.navy : T.textSec, fontSize: 12, fontWeight: on ? 700 : 500, cursor: "pointer", fontFamily: font, whiteSpace: "nowrap", flexShrink: 0 }}>
              <I d={t.d} size={13} color={on ? T.accent : T.textSec} />{t.label}
            </button>
          ); })}
        </div>
      </div>
      <div style={{ padding: 20, maxWidth: 640, margin: "0 auto" }}>{ActivePanel && <ActivePanel />}</div>

      {/* Certifications */}
      <div style={{ margin: "0 16px 20px", padding: 20, borderRadius: 14, background: T.bg, border: `1px solid ${T.border}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}><I d={ic.shield} size={15} color={T.accent} /><h3 style={{ fontSize: 15, fontWeight: 700, color: T.navy, margin: 0 }}>{it?"Certificazioni & Conformit\u00e0":"Certifications & Compliance"}</h3></div>
        {p.certs.map((c,i)=>(<div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "12px 0", borderBottom: i < p.certs.length-1 ? `1px solid ${T.borderLight}` : "none" }}><I d={ic.check} size={14} color={T.accent} /><div><div style={{ fontSize: 13, fontWeight: 600, color: T.textDark }}>{c.name}</div><div style={{ fontSize: 11, color: T.textSec }}>{c.num} {"·"} {c.issuer} {"·"} {c.valid}</div></div></div>))}
      </div>

      {/* Footer */}
      <div style={{ background: T.navy, padding: "24px 20px", borderTop: `3px solid ${T.accent}` }}>
        <div style={{ textAlign: "center", marginBottom: 10 }}><span style={{ fontSize: 18, fontWeight: 800, color: "#F1F5F9" }}>Dee<span style={{ color: T.accent }}>PP</span>y</span></div>
        <p style={{ textAlign: "center", fontSize: 11, color: T.textSec, lineHeight: 1.6, maxWidth: 380, margin: "0 auto 14px" }}>{it?"Passaporto Digitale di Prodotto conforme al Regolamento ESPR (UE) 2024/1781.":"Digital Product Passport compliant with ESPR Regulation (EU) 2024/1781."}</p>
        <div style={{ display: "flex", justifyContent: "center", gap: 16, fontSize: 11, color: T.textSec }}><span>{p.lastUpdated}</span><span>{p.version}</span></div>
        <div style={{ textAlign: "center", marginTop: 14, paddingTop: 14, borderTop: `1px solid ${T.navyLight}`, fontSize: 10 }}>
          {onNavigate ? <button onClick={()=>onNavigate("app")} style={{ background: "none", border: "none", color: T.accent, fontSize: 10, fontWeight: 600, cursor: "pointer", fontFamily: font }}>{it?"\u2190 Torna alla piattaforma":"\u2190 Back to platform"}</button> : <span style={{ color: T.textSec }}>deeppy.eu {"·"} Powered by Levery S.r.l.</span>}
        </div>
      </div>
    </div>
  );
}

export default function DeePPy() {
  const [page, setPage] = useState("landing");
  // Default language is English; remember the user's choice across refreshes.
  const [lang, setLang] = useState(() => {
    try { return localStorage.getItem("dpp_lang") || "en"; } catch { return "en"; }
  });
  useEffect(() => { try { localStorage.setItem("dpp_lang", lang); } catch {} }, [lang]);
  const L = { lang, setLang };

  // ── Authentication ──
  const [user, setUser] = useState(null);          // null = not logged in
  const [authChecked, setAuthChecked] = useState(false);

  // ── Product + Project DPP state (persisted via the backend DB) ──
  const [products, setProducts] = useState([]);       // list of General DPPs
  const [activeProductId, setActiveProductId] = useState(null);

  const activeProduct = products.find(p => p.id === activeProductId) || null;

  // Map an API product (summary or detail) → the shape the UI components expect.
  const apiToProduct = (api) => ({
    id: api.id,
    name: api.name,
    manufacturer: api.manufacturer || "",
    status: api.status || "draft",
    completeness: Math.round(api.completeness || 0),
    createdAt: api.created_at || new Date().toISOString(),
    updatedAt: api.updated_at || api.created_at || null,
    // dppData is null in list view; populated when detail is loaded.
    dppData: api.passport ? { passport: api.passport, stats: api.stats || null } : null,
    documents: api.documents || [],          // uploaded source files (filename, size_bytes)
    sourceDocuments: api.source_documents || [],
    // If any uploaded file is an image, surface it as the product image URL.
    imageUrl: (() => {
      const imgExt = /\.(jpe?g|png|webp|gif|bmp|tiff?)$/i;
      const d = (api.documents || []).find(x => imgExt.test(x.filename || ""));
      return d ? `/api/products/${api.id}/documents/${d.id}` : null;
    })(),
    projectDPPs: (api.batches || []).map(b => ({
      id: b.id, batch: b.lot || "", site: b.site || "", ref: b.ref || "",
      dims: "", weight: "", createdAt: b.created_at, items: b.items || [],
    })),
  });

  // Load the product list from the DB (only when authenticated).
  const loadProducts = useCallback(() => {
    fetch("/api/products", { credentials: "include" })
      .then(r => r.ok ? r.json() : [])
      .then(list => { if (Array.isArray(list)) setProducts(list.map(apiToProduct)); })
      .catch(() => {});
  }, []);

  // Check the session on mount; load products if a valid session exists.
  // If the user is already authenticated, jump straight to the dashboard
  // instead of leaving them on the public landing page (refresh-friendly).
  useEffect(() => {
    fetch("/api/auth/me", { credentials: "include" })
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d?.user) {
          setUser(d.user);
          loadProducts();
          setPage(prev => (prev === "landing" || prev === "signup" || prev === "login") ? "dashboard" : prev);
        }
      })
      .catch(() => {})
      .finally(() => setAuthChecked(true));
  }, [loadProducts]);

  // Called after a successful login/register.
  const handleAuth = (u) => { setUser(u); loadProducts(); setPage("dashboard"); };

  // Logout: clear the session cookie, then reset to the public landing.
  const handleLogout = async () => {
    try { await fetch("/api/auth/logout", { method: "POST", credentials: "include" }); } catch {}
    setUser(null); setProducts([]); setActiveProductId(null); setPage("landing");
  };

  // Fetch the full passport for one product (on navigate into it).
  const loadProductDetail = useCallback((id) => {
    fetch(`/api/products/${id}`, { credentials: "include" })
      .then(r => r.json())
      .then(api => {
        if (api && api.id) setProducts(prev => prev.map(p => p.id === id ? apiToProduct(api) : p));
      })
      .catch(() => {});
  }, []);

  // Called when AI extraction completes — the backend has already persisted the
  // product; we use its id and the returned passport/stats directly.
  const handleExtracted = (dppData) => {
    const pp = dppData?.passport;
    const pid = dppData?.product_id || ("prod-" + Date.now());
    const newProduct = apiToProduct({
      id: pid,
      name: pp?.overview?.product_info?.product_name?.value || "New Product",
      manufacturer: pp?.overview?.manufacturer?.company_name?.value || "",
      status: "draft",
      completeness: dppData?.stats?.completeness ?? 0,
      passport: pp,
      stats: dppData?.stats,
      created_at: new Date().toISOString(),
    });
    setProducts(prev => [...prev.filter(p => p.id !== pid), newProduct]);
    setActiveProductId(pid);
    // The extraction result has no `documents` array (it's just passport+stats),
    // so fetch the full detail to pull in the uploaded image / BoM / PDFs and
    // populate `imageUrl`. Otherwise the image only appears after a page reload.
    if (dppData?.product_id) loadProductDetail(dppData.product_id);
  };

  // Called from Progetto tab — creates a Project DPP (batch) on the backend.
  const handleAddProjectDPP = async (projData) => {
    if (!activeProductId) return null;
    try {
      const res = await fetch(`/api/products/${activeProductId}/batches`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lot: projData.batch, site: projData.site, ref: projData.ref,
          production_date: projData.date, notes: projData.notes,
        }),
      });
      const batch = await res.json();
      if (batch?.error) return null;
      const proj = {
        id: batch.id, batch: batch.lot || "", site: batch.site || "",
        ref: batch.ref || "", dims: projData.dims || "", weight: projData.weight || "",
        createdAt: batch.created_at,
      };
      setProducts(prev => prev.map(p =>
        p.id === activeProductId
          ? { ...p, projectDPPs: [...(p.projectDPPs || []), proj] }
          : p
      ));
      return proj.id;
    } catch {
      return null;
    }
  };

  // Save edits to a product's passport (PATCH) + refresh from server.
  const handleSaveProduct = async (productId, passport, changeSummary) => {
    try {
      const res = await fetch(`/api/products/${productId}`, {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ passport, change_summary: changeSummary || null }),
      });
      const api = await res.json();
      if (api?.id) setProducts(prev => prev.map(p => p.id === productId ? apiToProduct(api) : p));
      return true;
    } catch {
      return false;
    }
  };

  // Publish a product (status → published) via the backend.
  const handlePublish = async (productId) => {
    try {
      const res = await fetch(`/api/products/${productId}`, {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "published" }),
      });
      const api = await res.json();
      if (api?.id) setProducts(prev => prev.map(p => p.id === productId ? { ...p, status: "published" } : p));
      return true;
    } catch {
      return false;
    }
  };

  // Navigate to a product (from dashboard) — lazy-load its passport.
  // Delete a product (admin only on the backend) + drop it from local state.
  const handleDeleteProduct = async (productId) => {
    try {
      const res = await fetch(`/api/products/${productId}`, { method: "DELETE", credentials: "include" });
      if (!res.ok) return false;
      setProducts(prev => prev.filter(p => p.id !== productId));
      if (activeProductId === productId) setActiveProductId(null);
      return true;
    } catch {
      return false;
    }
  };

  const navigateToProduct = (productId, view) => {
    setActiveProductId(productId);
    setPage(view || "app-edit");
    const prod = products.find(p => p.id === productId);
    if (!prod || !prod.dppData) loadProductDetail(productId);
  };

  // Pages that require a valid session. Unauthenticated access → login screen.
  const PROTECTED = new Set([
    "onboard", "onboard-batch", "onboard-item", "dashboard", "catalog",
    "projects", "documents", "team", "settings", "app-edit", "app",
  ]);

  const content = (() => {
    // Gate protected pages behind authentication (wait for the session check first).
    if (PROTECTED.has(page)) {
      if (!authChecked) return <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: font, color: T.textSec }}>…</div>;
      if (!user) return <SignupPage onNavigate={setPage} L={L} onAuth={handleAuth} />;
    }
    switch (page) {
      case "landing": return <NewLandingPage onNavigate={setPage} L={L} />;
      case "signup": case "login": return <SignupPage onNavigate={setPage} L={L} onAuth={handleAuth} />;
      case "onboard": return <OnboardingUpload onNavigate={setPage} L={L} onExtracted={handleExtracted} />;
      case "onboard-batch": return <OnboardingUpload onNavigate={setPage} L={L} onExtracted={handleExtracted} presetType="batch" />;
      case "onboard-item": return <OnboardingUpload onNavigate={setPage} L={L} onExtracted={handleExtracted} presetType="item" />;
      case "dashboard": return <DashboardView onNavigate={setPage} L={L} products={products} onSelectProduct={navigateToProduct} onDelete={handleDeleteProduct} onLogout={handleLogout} user={user} />;
      case "catalog": return <CatalogView onNavigate={setPage} L={L} onLogout={handleLogout} user={user} />;
      case "projects": return <ProjectsView onNavigate={setPage} L={L} products={products} onLogout={handleLogout} user={user} />;
      case "documents": return <DocumentsView onNavigate={setPage} L={L} onLogout={handleLogout} user={user} />;
      case "team": return <TeamView onNavigate={setPage} L={L} onLogout={handleLogout} user={user} />;
      case "settings": return <SettingsView onNavigate={setPage} L={L} onLogout={handleLogout} user={user} />;
      case "app-edit": return <AppEditView onNavigate={setPage} L={L} dppData={activeProduct?.dppData} product={activeProduct} onAddProjectDPP={handleAddProjectDPP} onSave={handleSaveProduct} />;
      case "app": return <AppView onNavigate={setPage} L={L} product={activeProduct} onAddProjectDPP={handleAddProjectDPP} onPublish={handlePublish} />;
      case "public-dpp": return (
        <div style={{ minHeight: "100vh", background: T.navy, display: "flex", justifyContent: "center", padding: "20px 0" }}>
          <div style={{ width: "100%", maxWidth: "min(780px, 92vw)", background: T.bg, borderRadius: 16, overflow: "hidden", boxShadow: "0 25px 60px rgba(0,0,0,0.3)" }}>
            <PublicDPPView onNavigate={setPage} L={L} dppData={activeProduct?.dppData} imageUrl={activeProduct?.imageUrl} />
          </div>
        </div>
      );
      default: return <NewLandingPage onNavigate={setPage} L={L} />;
    }
  })();
  return <>{content}<CookieBanner lang={lang} /></>;
}
