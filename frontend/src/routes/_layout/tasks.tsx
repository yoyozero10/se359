import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { TasksService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddTask from "@/components/Tasks/AddTask"
import { columns } from "@/components/Tasks/columns"
import PendingItems from "@/components/Pending/PendingItems"

function getTasksQueryOptions() {
  return {
    queryFn: () => TasksService.readTasks({ skip: 0, limit: 100 }),
    queryKey: ["Tasks"],
  }
}

export const Route = createFileRoute("/_layout/tasks")({
  component: Tasks,
  head: () => ({
    meta: [
      {
        title: "Tasks - FastAPI Template",
      },
    ],
  }),
})

function TasksTableContent() {
  const { data: Tasks } = useSuspenseQuery(getTasksQueryOptions())

  if (Tasks.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any Tasks yet</h3>
        <p className="text-muted-foreground">Add a new Task to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={Tasks.data} />
}

function TasksTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <TasksTableContent />
    </Suspense>
  )
}

function Tasks() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tasks</h1>
          <p className="text-muted-foreground">Create and manage your Tasks</p>
        </div>
        <AddTask />
      </div>
      <TasksTable />
    </div>
  )
}

