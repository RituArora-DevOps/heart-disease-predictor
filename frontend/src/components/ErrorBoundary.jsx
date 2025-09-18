import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() {
    return { hasError: true }
  }
  componentDidCatch(err, info) {
    console.error(err, info)
  }
  render() {
    if (this.state.hasError) {
      return <div className="card text-center">Something went wrong. Please refresh.</div>
    }
    return this.props.children
  }
}
