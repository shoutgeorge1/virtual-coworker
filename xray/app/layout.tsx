import type { ReactNode } from "react";

/** Minimal layout — dashboard UI remains static HTML in public/. */
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
