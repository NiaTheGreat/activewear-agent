"use client";

import { LoginForm } from "@/components/auth/LoginForm";
import { PageTransition } from "@/components/layout/PageTransition";

export default function LoginPage() {
  return (
    <PageTransition>
      <div className="space-y-2 text-center mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
          Welcome back
        </h1>
        <p className="text-sm text-gray-500">
          Sign in to your account to continue
        </p>
      </div>
      <LoginForm />
    </PageTransition>
  );
}
