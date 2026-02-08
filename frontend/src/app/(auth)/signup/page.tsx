"use client";

import { SignupForm } from "@/components/auth/SignupForm";
import { PageTransition } from "@/components/layout/PageTransition";

export default function SignupPage() {
  return (
    <PageTransition>
      <div className="space-y-2 text-center mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
          Create an account
        </h1>
        <p className="text-sm text-gray-500">
          Get started with manufacturer discovery
        </p>
      </div>
      <SignupForm />
    </PageTransition>
  );
}
