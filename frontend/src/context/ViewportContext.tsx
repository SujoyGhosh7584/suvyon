import { createContext, ReactNode, useContext, useEffect, useState } from "react";

const MOBILE_QUERY = "(max-width: 767px)";

const ViewportContext = createContext<boolean | undefined>(undefined);

function readIsMobile() {
  if (typeof window === "undefined") return false;
  return window.matchMedia(MOBILE_QUERY).matches;
}

export function ViewportProvider({ children }: { children: ReactNode }) {
  const [isMobile, setIsMobile] = useState(readIsMobile);

  useEffect(() => {
    const media = window.matchMedia(MOBILE_QUERY);
    const onChange = () => setIsMobile(media.matches);
    onChange();
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return <ViewportContext.Provider value={isMobile}>{children}</ViewportContext.Provider>;
}

export function useIsMobile() {
  const value = useContext(ViewportContext);
  if (value === undefined) {
    return readIsMobile();
  }
  return value;
}
