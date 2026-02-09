"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
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
} from "lucide-react";
import { OrganizationSwitcher } from "@/components/organization/OrganizationSwitcher";
import { useOrganizationStore } from "@/store/organizationStore";
import { Separator } from "@/components/ui/separator";

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

export function Sidebar() {
  const pathname = usePathname();
  const { currentOrganization, isPersonalWorkspace } = useOrganizationStore();

  const navItems = isPersonalWorkspace() ? personalNavItems : organizationNavItems;

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:border-r lg:border-gray-200 lg:bg-white">
      {/* Organization Switcher */}
      <div className="px-3 py-4">
        <OrganizationSwitcher />
      </div>

      <Separator />

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
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
    </aside>
  );
}
