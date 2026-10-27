// Emblème officiel Novissi-Droit (public/logo-mark.png), fond transparent : fonctionne en thème clair et sombre.
export default function NovissiLogo({ size = 34, animated = false }: { size?: number; animated?: boolean }) {
  return (
    <img
      src="/logo-mark.png"
      alt=""
      aria-hidden="true"
      width={size}
      height={Math.round((size * 143) / 146)}
      className={animated ? "novissi-mark novissi-mark--hero" : "novissi-mark"}
      draggable={false}
    />
  );
}
