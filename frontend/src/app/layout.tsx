import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

import { AuthProvider } from "@/components/auth-provider";
import { ChromeShell } from "@/components/layout/chrome-shell";

export const metadata: Metadata = {
  title: "clipsmith | Social Video Platform",
  description: "The premier social video creation platform.",
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  viewportFit: 'cover',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-zinc-50 dark:bg-zinc-950 text-zinc-950 dark:text-zinc-50`}
      >
        <AuthProvider>
          <ChromeShell>{children}</ChromeShell>
        </AuthProvider>
      </body>
    </html>
  );
}
