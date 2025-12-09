"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { Lock, Loader2, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ResetPasswordPage() {
  const t = useTranslations("auth");
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [token, setToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  useEffect(() => {
    const tokenParam = searchParams.get("token");
    if (!tokenParam) {
      toast.error(t("invalidResetLink"));
      router.push("/auth/forgot-password");
    } else {
      setToken(tokenParam);
    }
  }, [searchParams, router, t]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast.error(t("passwordsDoNotMatch"));
      return;
    }

    if (newPassword.length < 8) {
      toast.error(t("passwordTooShort"));
      return;
    }

    if (!token) {
      toast.error(t("invalidResetLink"));
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/password-reset/confirm`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          new_password: newPassword,
        }),
      });

      if (response.ok) {
        setResetSuccess(true);
        toast.success(t("passwordResetSuccess"));
        setTimeout(() => {
          router.push("/auth/sign-in");
        }, 3000);
      } else {
        const error = await response.json();
        toast.error(error.detail || t("passwordResetFailed"));
      }
    } catch (error) {
      toast.error(t("networkError"));
    } finally {
      setIsLoading(false);
    }
  };

  if (resetSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950 p-4">
        <Card className="w-full max-w-md border-zinc-800 bg-zinc-900">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 rounded-full bg-emerald-500/10">
                <CheckCircle className="h-12 w-12 text-emerald-400" />
              </div>
            </div>
            <CardTitle className="text-2xl">{t("passwordResetSuccess")}</CardTitle>
            <CardDescription className="text-zinc-400">
              {t("passwordResetSuccessDescription")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-center text-zinc-400 text-sm mb-4">
              {t("redirectingToSignIn")}
            </p>
            <Button asChild className="w-full bg-emerald-600 hover:bg-emerald-700">
              <Link href="/auth/sign-in">{t("signIn")}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950 p-4">
        <Card className="w-full max-w-md border-zinc-800 bg-zinc-900">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 rounded-full bg-red-500/10">
                <AlertCircle className="h-12 w-12 text-red-400" />
              </div>
            </div>
            <CardTitle className="text-2xl">{t("invalidResetLink")}</CardTitle>
            <CardDescription className="text-zinc-400">
              {t("invalidResetLinkDescription")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full" variant="outline">
              <Link href="/auth/forgot-password">{t("requestNewLink")}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 p-4">
      <Card className="w-full max-w-md border-zinc-800 bg-zinc-900">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl flex items-center gap-2">
            <Lock className="h-6 w-6 text-emerald-400" />
            {t("resetPassword")}
          </CardTitle>
          <CardDescription className="text-zinc-400">
            {t("resetPasswordDescription")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="newPassword">{t("newPassword")}</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                <Input
                  id="newPassword"
                  type="password"
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="pl-10 bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
                />
              </div>
              <p className="text-xs text-zinc-500">{t("passwordMinLength")}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">{t("confirmPassword")}</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-zinc-500" />
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={8}
                  className="pl-10 bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-emerald-600 hover:bg-emerald-700"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t("resetting")}
                </>
              ) : (
                t("resetPassword")
              )}
            </Button>

            <Button asChild variant="ghost" className="w-full">
              <Link href="/auth/sign-in">
                <ArrowLeft className="mr-2 h-4 w-4" />
                {t("backToSignIn")}
              </Link>
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

