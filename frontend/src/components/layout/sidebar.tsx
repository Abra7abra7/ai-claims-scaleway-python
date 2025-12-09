"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  LayoutDashboard,
  FileText,
  FolderOpen,
  FileBarChart,
  History,
  Settings,
  LogOut,
  ChevronDown,
  Globe,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { signOut, useSession } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

const navigation = [
  { name: "dashboard", href: "/", icon: LayoutDashboard },
  { name: "claims", href: "/claims", icon: FileText },
  { name: "rag", href: "/rag", icon: FolderOpen },
  { name: "reports", href: "/reports", icon: FileBarChart },
  { name: "audit", href: "/audit", icon: History },
  { name: "settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations("navigation");
  const tSettings = useTranslations("settings");
  const tAuth = useTranslations("auth");
  const { data: session } = useSession();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push("/auth/sign-in");
  };

  const setLocale = (locale: string) => {
    document.cookie = `locale=${locale};path=/;max-age=31536000`;
    window.location.reload();
  };

  return (
    <aside className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-zinc-800 bg-zinc-950">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b border-zinc-800 px-6">
        <Shield className="h-8 w-8 text-emerald-500" />
        <span className="text-lg font-semibold text-white">AI Claims</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== "/" && pathname.startsWith(item.href));
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:bg-zinc-800/50 hover:text-white"
              )}
            >
              <item.icon className="h-5 w-5" />
              {t(item.name)}
            </Link>
          );
        })}
      </nav>

      {/* Language Switcher */}
      <div className="border-t border-zinc-800 px-3 py-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-zinc-400 hover:bg-zinc-800/50 hover:text-white"
            >
              <Globe className="h-5 w-5" />
              {tSettings("language")}
              <ChevronDown className="ml-auto h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48">
            <DropdownMenuItem onClick={() => setLocale("sk")}>
              🇸🇰 {tSettings("languages.sk")}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setLocale("en")}>
              🇬🇧 {tSettings("languages.en")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* User Menu */}
      <div className="border-t border-zinc-800 p-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 px-3 py-2 text-left hover:bg-zinc-800/50"
            >
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-emerald-600 text-white">
                  {session?.user?.name?.[0]?.toUpperCase() || "U"}
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-col">
                <span className="text-sm font-medium text-white">
                  {session?.user?.name || "User"}
                </span>
                <span className="text-xs text-zinc-500">
                  {session?.user?.email || "user@example.com"}
                </span>
              </div>
              <ChevronDown className="ml-auto h-4 w-4 text-zinc-500" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem asChild>
              <Link href="/settings">
                <Settings className="mr-2 h-4 w-4" />
                {tSettings("title")}
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleSignOut} className="text-red-400">
              <LogOut className="mr-2 h-4 w-4" />
              {tAuth("signOut")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
}

