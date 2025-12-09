"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { Loader2, CheckCircle, AlertCircle, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function VerifyEmailPage() {
  const t = useTranslations("auth");
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [verifying, setVerifying] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    
    if (!token) {
      setError(t("invalidVerificationLink"));
      setVerifying(false);
      return;
    }

    verifyEmail(token);
  }, [searchParams, t]);

  const verifyEmail = async (token: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/verify-email/${token}`, {
        method: "GET",
        credentials: "include",
      });

      if (response.ok) {
        setSuccess(true);
        setTimeout(() => {
          router.push("/auth/sign-in");
        }, 3000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || t("verificationFailed"));
      }
    } catch (err) {
      setError(t("networkError"));
    } finally {
      setVerifying(false);
    }
  };

  if (verifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950 p-4">
        <Card className="w-full max-w-md border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6 text-center">
            <Loader2 className="h-12 w-12 animate-spin text-emerald-400 mx-auto mb-4" />
            <p className="text-zinc-400">{t("verifyingEmail")}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950 p-4">
        <Card className="w-full max-w-md border-zinc-800 bg-zinc-900">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-3 rounded-full bg-emerald-500/10">
                <CheckCircle className="h-12 w-12 text-emerald-400" />
              </div>
            </div>
            <CardTitle className="text-2xl">{t("emailVerified")}</CardTitle>
            <CardDescription className="text-zinc-400">
              {t("emailVerifiedDescription")}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-zinc-400 text-sm">
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

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 p-4">
      <Card className="w-full max-w-md border-zinc-800 bg-zinc-900">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full bg-red-500/10">
              <AlertCircle className="h-12 w-12 text-red-400" />
            </div>
          </div>
          <CardTitle className="text-2xl">{t("verificationFailed")}</CardTitle>
          <CardDescription className="text-zinc-400">
            {error || t("verificationFailedDescription")}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-center text-zinc-400 text-sm">
            {t("verificationLinkExpired")}
          </p>
          <Button asChild className="w-full" variant="outline">
            <Link href="/auth/sign-in">{t("backToSignIn")}</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

