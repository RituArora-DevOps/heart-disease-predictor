import { createContext, useContext, useState } from 'react'
const Ctx = createContext({ result: null, setResult: () => {} })
export function ResultProvider({ children }) {
  const [result, setResult] = useState(null)
  return <Ctx.Provider value={{ result, setResult }}>{children}</Ctx.Provider>
}
export function useResult() {
  return useContext(Ctx)
}
