export function minsAndSecs (d) {
  let mins_ = d / 60
  let mins = Math.trunc(mins_)
  let secs = Math.round((mins_ - mins) * 60).toString().padStart(2, '0')
  return `${mins}:${secs}`
}