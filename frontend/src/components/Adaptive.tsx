import type { ComponentType } from "react";
import { useIsMobile } from "@/context/ViewportContext";

export function Adaptive({
  mobile: Mobile,
  desktop: Desktop,
}: {
  mobile: ComponentType;
  desktop: ComponentType;
}) {
  const isMobile = useIsMobile();
  return isMobile ? <Mobile /> : <Desktop />;
}
