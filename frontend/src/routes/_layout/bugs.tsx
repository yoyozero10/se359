import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense } from "react"

import { BugsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddBug from "@/components/Bugs/AddBug"
import { columns } from "@/components/Bugs/columns"
import PendingItems from "@/components/Pending/PendingItems"

function getBugsQueryOptions() {
  return {
    queryFn: () => BugsService.readBugs({ skip: 0, limit: 100 }),
    queryKey: ["Bugs"],
  }
}

export const Route = createFileRoute("/_layout/bugs")({
  component: Bugs,
  head: () => ({
    meta: [
      {
        title: "Bugs - DevOps Manager",
      },
    ],
  }),
})

function BugsTableContent() {
  const { data: Bugs } = useSuspenseQuery(getBugsQueryOptions())

  if (Bugs.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any Bugs yet</h3>
        <p className="text-muted-foreground">Report a new Bug to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={Bugs.data} />
}

function BugsTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <BugsTableContent />
    </Suspense>
  )
}

function Bugs() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Bugs</h1>
          <p className="text-muted-foreground">Track and manage bugs</p>
        </div>
        <AddBug />
      </div>
      <BugsTable />
    </div>
  )
}
