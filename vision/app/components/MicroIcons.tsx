import type { JSX, ReactNode } from "react";
import type { CategorySlug } from "../../config/categories";

type IconProps = {
  className?: string;
};

function IconShell({
  className,
  children,
}: IconProps & { children: ReactNode }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      width="24"
      height="24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      {children}
    </svg>
  );
}

export function IconMegaphone({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <path d="M3 11v2a2 2 0 0 0 2 2h1l4 3V6L6 9H5a2 2 0 0 0-2 2Z" />
      <path d="M14.5 8.5a4.5 4.5 0 0 1 0 7" />
      <path d="M16.8 6.2a8 8 0 0 1 0 11.6" />
    </IconShell>
  );
}

export function IconShare({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <circle cx="18" cy="5" r="2.4" />
      <circle cx="6" cy="12" r="2.4" />
      <circle cx="18" cy="19" r="2.4" />
      <path d="M8.2 13.1 15.8 17.4M15.8 6.6 8.2 10.9" />
    </IconShell>
  );
}

export function IconCalculator({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <rect x="4" y="3" width="16" height="18" rx="2.5" />
      <path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01" />
    </IconShell>
  );
}

export function IconLedger({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <path d="M5 4.5h11.5A2.5 2.5 0 0 1 19 7v13H7.5A2.5 2.5 0 0 1 5 17.5Z" />
      <path d="M5 4.5A2.5 2.5 0 0 0 7.5 7V20.5" />
      <path d="M9.5 10h6M9.5 13.5h6M9.5 17h4" />
    </IconShell>
  );
}

export function IconClipboard({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <rect x="6" y="5" width="12" height="16" rx="2" />
      <path d="M9 5.2V4.5A1.5 1.5 0 0 1 10.5 3h3A1.5 1.5 0 0 1 15 4.5v.7" />
      <path d="M9 11h6M9 14.5h6M9 18h3.5" />
    </IconShell>
  );
}

export function IconHeadset({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <path d="M4.5 13v-1a7.5 7.5 0 0 1 15 0v1" />
      <path d="M4.5 13.5v3.2A1.8 1.8 0 0 0 6.3 18.5H7.5" />
      <path d="M19.5 13.5v3.2a1.8 1.8 0 0 1-1.8 1.8H16.5" />
      <path d="M12 18.5v1.2a1.8 1.8 0 0 0 1.8 1.8H15" />
    </IconShell>
  );
}

export function IconPeople({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <circle cx="9" cy="8" r="2.6" />
      <circle cx="16.5" cy="9" r="2.1" />
      <path d="M3.8 18.5c.6-3 2.7-4.5 5.2-4.5s4.6 1.5 5.2 4.5" />
      <path d="M14.2 14.3c1.6-.3 3.3.5 4.2 2.7" />
    </IconShell>
  );
}

export function IconSearchPerson({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <circle cx="10" cy="8.5" r="2.7" />
      <path d="M4.5 18.5c.6-2.9 2.6-4.4 5.5-4.4 1.4 0 2.6.4 3.5 1.1" />
      <circle cx="16.5" cy="15.5" r="2.6" />
      <path d="M18.4 17.4 21 20" />
    </IconShell>
  );
}

export function IconGrowth({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <path d="M4 19h16" />
      <path d="M7 16V11" />
      <path d="M12 16V7" />
      <path d="M17 16V9.5" />
      <path d="M14.5 6.5 17 4l2.5 2.5" />
    </IconShell>
  );
}

export function IconChat({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <path d="M5 6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5v6A2.5 2.5 0 0 1 16.5 15H11l-4 3.2V15H7.5A2.5 2.5 0 0 1 5 12.5Z" />
      <path d="M9 9h6M9 12h3.5" />
    </IconShell>
  );
}

export function IconBrief({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <rect x="4" y="7" width="16" height="12.5" rx="2" />
      <path d="M9 7V5.8A1.8 1.8 0 0 1 10.8 4h2.4A1.8 1.8 0 0 1 15 5.8V7" />
      <path d="M4 12h16" />
    </IconShell>
  );
}

export function IconChoose({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <circle cx="12" cy="8" r="3" />
      <path d="M5.5 19c.8-3.2 3-4.8 6.5-4.8s5.7 1.6 6.5 4.8" />
      <path d="M16.2 6.2 18 8l3-3.2" />
    </IconShell>
  );
}

export function IconStart({ className }: IconProps) {
  return (
    <IconShell className={className}>
      <circle cx="12" cy="12" r="8.2" />
      <path d="M10.2 9.2 15.3 12l-5.1 2.8Z" fill="currentColor" stroke="none" />
    </IconShell>
  );
}

const SERVICE_ICONS: Record<
  CategorySlug,
  (props: IconProps) => JSX.Element
> = {
  "digital-marketing": IconMegaphone,
  "social-media": IconShare,
  accounting: IconCalculator,
  bookkeeping: IconLedger,
  "administrative-support": IconClipboard,
  "customer-service": IconHeadset,
  hr: IconPeople,
  recruitment: IconSearchPerson,
  sales: IconGrowth,
};

export function ServiceIcon({
  slug,
  className,
}: {
  slug: CategorySlug;
  className?: string;
}) {
  const Icon = SERVICE_ICONS[slug];
  return <Icon className={className} />;
}

export const HOW_STEP_ICONS = [
  IconChat,
  IconBrief,
  IconChoose,
  IconStart,
] as const;
