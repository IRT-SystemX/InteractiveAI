import type { Entity, TaskTypes } from './entities'

export type Step<E extends Entity = Entity> = {
  taskIndex: number
  taskText: string
  taskType: TaskTypes<E>
  state?: 'doing' | 'done'
}

export type Block<E extends Entity = Entity> = {
  blockIndex: number
  blockText: string
  tasks: Step<E>[]
}

export type Procedure<E extends Entity = Entity> = {
  max_speed: number
  min_speed: number
  procedure: Block<E>[]
}
