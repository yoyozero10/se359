import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { TaskPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteTask from "../Tasks/DeleteTask"
import EditTask from "../Tasks/EditTask"

interface TaskActionsMenuProps {
  Task: TaskPublic
}

export const TaskActionsMenu = ({ Task }: TaskActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditTask Task={Task} onSuccess={() => setOpen(false)} />
        <DeleteTask id={Task.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

