"use client";

import { useOrganizationStore } from "@/store/organizationStore";
import { usePipelines } from "@/hooks/usePipelines";
import { useOrganizationMembers } from "@/hooks/useOrganizations";
import { EmptyState } from "@/components/common/EmptyState";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CreatePipelineDialog } from "@/components/pipeline/CreatePipelineDialog";
import { PipelineCard } from "@/components/pipeline/PipelineCard";
import Link from "next/link";
import { Building2, Users, FolderKanban, Search, ArrowRight } from "lucide-react";

export default function TeamDashboardPage() {
  const { currentOrganization, isPersonalWorkspace } = useOrganizationStore();
  const { data: pipelines, isLoading: pipelinesLoading } = usePipelines(currentOrganization?.id);
  const { data: members } = useOrganizationMembers(currentOrganization?.id);

  if (isPersonalWorkspace() || !currentOrganization) {
    return (
      <div className="container mx-auto max-w-6xl px-4 py-8">
        <EmptyState
          icon={Building2}
          title="No organization selected"
          description="Please select an organization to view the team dashboard"
        />
      </div>
    );
  }

  const totalManufacturers = pipelines?.reduce(
    (sum, pipeline) => sum + (pipeline.manufacturer_count || 0),
    0
  ) || 0;

  return (
    <div className="container mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">{currentOrganization.name}</h1>
        <p className="mt-1 text-muted-foreground">
          {currentOrganization.description || "Team workspace for manufacturer research"}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{members?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active collaborators
            </p>
            <Link href="/dashboard/org/members">
              <Button variant="link" className="mt-2 h-auto p-0 text-xs">
                Manage members →
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pipelines</CardTitle>
            <FolderKanban className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pipelines?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active collections
            </p>
            <Link href="/dashboard/org/pipelines">
              <Button variant="link" className="mt-2 h-auto p-0 text-xs">
                View pipelines →
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Manufacturers</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalManufacturers}</div>
            <p className="text-xs text-muted-foreground">
              Across all pipelines
            </p>
            <Link href="/dashboard/org/manufacturers">
              <Button variant="link" className="mt-2 h-auto p-0 text-xs">
                View all →
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Link href="/search/new">
            <Button>
              <Search className="mr-2 h-4 w-4" />
              Run Team Search
            </Button>
          </Link>
          {currentOrganization.id && (
            <CreatePipelineDialog
              organizationId={currentOrganization.id}
              trigger={
                <Button variant="outline">
                  <FolderKanban className="mr-2 h-4 w-4" />
                  Create Pipeline
                </Button>
              }
            />
          )}
          <Link href="/dashboard/org/members">
            <Button variant="outline">
              <Users className="mr-2 h-4 w-4" />
              Invite Members
            </Button>
          </Link>
        </div>
      </div>

      {/* Pipelines Section */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Recent Pipelines</h2>
          <Link href="/dashboard/org/pipelines">
            <Button variant="ghost" size="sm">
              View all
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        {pipelinesLoading ? (
          <div className="text-center text-sm text-muted-foreground">
            Loading pipelines...
          </div>
        ) : !pipelines || pipelines.length === 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>No pipelines yet</CardTitle>
              <CardDescription>
                Create your first pipeline to start organizing manufacturers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CreatePipelineDialog
                organizationId={currentOrganization.id}
                trigger={<Button>Create First Pipeline</Button>}
              />
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {pipelines.slice(0, 6).map((pipeline) => (
              <PipelineCard key={pipeline.id} pipeline={pipeline} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
