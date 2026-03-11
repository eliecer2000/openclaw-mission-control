export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (raw && raw.toLowerCase() !== "auto") {
    return (
      raw.replace(/\/+$/, "") ||
      (() => {
        throw new Error("NEXT_PUBLIC_API_URL is invalid.");
      })()
    );
  }

  if (typeof window !== "undefined") {
    const protocol = window.location.protocol; // "https:" or "http:"
    const host = window.location.hostname;
    const port = window.location.port;
    const isStandardPort =
      (protocol === "https:" && (port === "443" || port === "")) ||
      (protocol === "http:" && (port === "80" || port === ""));
    if (host) {
      return isStandardPort
        ? `${protocol}//${host}`
        : `${protocol}//${host}:${port}`;
    }
  }

  throw new Error(
    "NEXT_PUBLIC_API_URL is not set and cannot be auto-resolved outside the browser.",
  );
}
