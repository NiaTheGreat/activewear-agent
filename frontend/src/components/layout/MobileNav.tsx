"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { OrganizationSwitcher } from "@/components/organization/OrganizationSwitcher";
import { useOrganizationStore } from "@/store/organizationStore";
import {
  LayoutDashboard,
  Search,
  Clock,
  Bookmark,
  Factory,
  Heart,
  Kanban,
  Users,
  FolderKanban,
  Menu,
} from "lucide-react";

const personalNavItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/search/new", label: "New Search", icon: Search },
  { href: "/manufacturers", label: "All Manufacturers", icon: Factory },
  { href: "/favorites", label: "Favorites", icon: Heart },
  { href: "/pipeline", label: "Pipeline", icon: Kanban },
  { href: "/history", label: "History", icon: Clock },
  { href: "/presets", label: "Presets", icon: Bookmark },
];

const organizationNavItems = [
  { href: "/dashboard/org", label: "Team Dashboard", icon: LayoutDashboard },
  { href: "/search/new", label: "New Search", icon: Search },
  { href: "/dashboard/org/pipelines", label: "Pipelines", icon: FolderKanban },
  { href: "/dashboard/org/manufacturers", label: "Manufacturers", icon: Factory },
  { href: "/dashboard/org/history", label: "Search History", icon: Clock },
  { href: "/dashboard/org/members", label: "Members", icon: Users },
];

export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { currentOrganization, isPersonalWorkspace } = useOrganizationStore();

  const navItems = isPersonalWorkspace() ? personalNavItems : organizationNavItems;

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="lg:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-72 p-0">
        <SheetHeader className="p-4 pb-0">
          <SheetTitle className="text-left">Navigation</SheetTitle>
        </SheetHeader>

        {/* Organization Switcher */}
        <div className="px-4 py-4">
          <OrganizationSwitcher />
        </div>

        <Separator />

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-4 py-4">
          {!isPersonalWorkspace() && currentOrganization && (
            <div className="mb-3 px-3">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {currentOrganization.name}
              </p>
            </div>
          )}

          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" &&
               item.href !== "/dashboard/org" &&
               pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary-50 text-primary-700"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                )}
              >
                <item.icon
                  className={cn(
                    "h-5 w-5",
                    isActive ? "text-primary-600" : "text-gray-400"
                  )}
                />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </SheetContent>
    </Sheet>
  );
}
