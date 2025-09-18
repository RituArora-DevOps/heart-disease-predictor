export default function Button({ className = '', size = 'md', ...props }) {
  const sizing =
    size === 'lg'
      ? 'px-6 md:px-7 py-3 md:py-3.5 text-[13px] md:text-base'
      : 'px-5 py-2 text-[13px] md:text-sm'

  return (
    <button
      {...props}
      className={`bg-accent inline-flex items-center justify-center rounded-lg font-bold tracking-widest text-white shadow-sm transition hover:opacity-95 disabled:opacity-60 ${sizing} ${className}`}
    />
  )
}
