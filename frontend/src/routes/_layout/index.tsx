import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import {
  Briefcase,
  CheckSquare,
  Bug,
  AlertTriangle,
  Activity,
  Server,
  GitCommit,
  Clock,
} from "lucide-react"

import {
  ProjectsService,
  TasksService,
  BugsService,
  IncidentsService,
  DevopsService,
} from "@/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - DevOps Manager",
      },
    ],
  }),
})

function StatCard({
  title,
  value,
  icon: Icon,
  description,
  loading,
  variant = "default",
}: {
  title: string
  value: string | number
  icon: React.ElementType
  description?: string
  loading?: boolean
  variant?: "default" | "success" | "warning" | "danger"
}) {
  const variantClasses = {
    default: "bg-card",
    success: "bg-card border-green-500/20",
    warning: "bg-card border-yellow-500/20",
    danger: "bg-card border-red-500/20",
  }

  const iconClasses = {
    default: "text-muted-foreground",
    success: "text-green-500",
    warning: "text-yellow-500",
    danger: "text-red-500",
  }

  return (
    <Card className={variantClasses[variant]}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${iconClasses[variant]}`} />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-16" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryFn: () => ProjectsService.readProjects({ skip: 0, limit: 100 }),
    queryKey: ["dashboard-projects"],
  })

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryFn: () => TasksService.readTasks({ skip: 0, limit: 100 }),
    queryKey: ["dashboard-tasks"],
  })

  const { data: bugs, isLoading: bugsLoading } = useQuery({
    queryFn: () => BugsService.readBugs({ skip: 0, limit: 100 }),
    queryKey: ["dashboard-bugs"],
  })

  const { data: incidents, isLoading: incidentsLoading } = useQuery({
    queryFn: () => IncidentsService.readIncidents({ skip: 0, limit: 100 }),
    queryKey: ["dashboard-incidents"],
  })

  const { data: versionInfo, isLoading: versionLoading } = useQuery({
    queryFn: () => DevopsService.version(),
    queryKey: ["dashboard-version"],
  })

  const { data: healthInfo, isLoading: healthLoading } = useQuery({
    queryFn: () => DevopsService.healthz(),
    queryKey: ["dashboard-health"],
  })

  // Compute stats
  const tasksByStatus = {
    todo: tasks?.data?.filter((t) => t.status === "todo").length ?? 0,
    in_progress: tasks?.data?.filter((t) => t.status === "in_progress").length ?? 0,
    done: tasks?.data?.filter((t) => t.status === "done").length ?? 0,
  }

  const openBugs = bugs?.data?.filter((b) => b.status === "open" || b.status === "in_progress").length ?? 0
  const openIncidents = incidents?.data?.filter((i) => i.status !== "resolved").length ?? 0

  const version = versionInfo as any
  const health = healthInfo as any

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground">
          Welcome to your DevOps Dashboard. Here's an overview of your system.
        </p>
      </div>

      {/* System Status */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Server className="h-5 w-5" />
          System Status
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Health</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {healthLoading ? (
                <Skeleton className="h-6 w-12" />
              ) : (
                <Badge variant={health?.status === "ok" ? "default" : "destructive"}>
                  {health?.status ?? "unknown"}
                </Badge>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Version</CardTitle>
              <GitCommit className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {versionLoading ? (
                <Skeleton className="h-6 w-20" />
              ) : (
                <div>
                  <div className="text-lg font-bold">{version?.version ?? "—"}</div>
                  <p className="text-xs text-muted-foreground font-mono mt-1">
                    {version?.commit_sha ?? "—"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Environment</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {versionLoading ? (
                <Skeleton className="h-6 w-16" />
              ) : (
                <Badge variant="outline">{version?.environment ?? "—"}</Badge>
              )}
            </CardContent>
          </Card>

          <StatCard
            title="Total Projects"
            value={projects?.count ?? 0}
            icon={Briefcase}
            loading={projectsLoading}
          />
        </div>
      </div>

      {/* Work Items Overview */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <CheckSquare className="h-5 w-5" />
          Work Items Overview
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Tasks: To Do"
            value={tasksByStatus.todo}
            icon={CheckSquare}
            loading={tasksLoading}
            description={`${tasks?.count ?? 0} total tasks`}
          />
          <StatCard
            title="Tasks: In Progress"
            value={tasksByStatus.in_progress}
            icon={CheckSquare}
            loading={tasksLoading}
            variant="warning"
          />
          <StatCard
            title="Tasks: Done"
            value={tasksByStatus.done}
            icon={CheckSquare}
            loading={tasksLoading}
            variant="success"
          />
          <StatCard
            title="Open Bugs"
            value={openBugs}
            icon={Bug}
            loading={bugsLoading}
            description={`${bugs?.count ?? 0} total bugs`}
            variant={openBugs > 0 ? "danger" : "success"}
          />
        </div>
      </div>

      {/* Incidents */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          Incidents
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <StatCard
            title="Open Incidents"
            value={openIncidents}
            icon={AlertTriangle}
            loading={incidentsLoading}
            variant={openIncidents > 0 ? "danger" : "success"}
            description={openIncidents > 0 ? "Requires attention" : "All clear!"}
          />
          <StatCard
            title="Total Incidents"
            value={incidents?.count ?? 0}
            icon={AlertTriangle}
            loading={incidentsLoading}
          />
          <StatCard
            title="Resolved"
            value={
              (incidents?.count ?? 0) - openIncidents
            }
            icon={AlertTriangle}
            loading={incidentsLoading}
            variant="success"
          />
        </div>
      </div>

      {/* Recent Activity placeholder */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Quick Summary
        </h2>
        <Card>
          <CardContent className="pt-6">
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-primary/10 p-2">
                  <Briefcase className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">{projects?.count ?? 0} Projects</p>
                  <p className="text-xs text-muted-foreground">Active projects</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-blue-500/10 p-2">
                  <CheckSquare className="h-4 w-4 text-blue-500" />
                </div>
                <div>
                  <p className="text-sm font-medium">{tasks?.count ?? 0} Tasks</p>
                  <p className="text-xs text-muted-foreground">{tasksByStatus.in_progress} in progress</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-orange-500/10 p-2">
                  <Bug className="h-4 w-4 text-orange-500" />
                </div>
                <div>
                  <p className="text-sm font-medium">{bugs?.count ?? 0} Bugs</p>
                  <p className="text-xs text-muted-foreground">{openBugs} open</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-red-500/10 p-2">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                </div>
                <div>
                  <p className="text-sm font-medium">{incidents?.count ?? 0} Incidents</p>
                  <p className="text-xs text-muted-foreground">{openIncidents} unresolved</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
