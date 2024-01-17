export const Entities =  ["ORANGE","DA","SNCF","RTE"] as const

export type Entity = typeof Entities[number]
