import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { BugPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteBug from "./DeleteBug"
import EditBug from "./EditBug"

interface BugActionsMenuProps {
  Bug: BugPublic
}

export const BugActionsMenu = ({ Bug }: BugActionsMenuProps) => {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditBug Bug={Bug} onSuccess={() => setOpen(false)} />
        <DeleteBug id={Bug.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
