const HOUR_IN_SECONDS = 3600
const MINUTE_IN_SECONDS = 60

export { HOUR_IN_SECONDS, MINUTE_IN_SECONDS }

export function parseSinceToSeconds(value) {
  const rawValue = value.trim().toLowerCase()
  const match = rawValue.match(/^(\d+)([hm])$/)

  if (!match) {
    return null
  }

  const amount = Number(match[1])
  const unit = match[2]

  return unit === 'h'
    ? amount * HOUR_IN_SECONDS
    : amount * MINUTE_IN_SECONDS
}

export function getAlignedRange(value) {
  const nowInSeconds = Math.floor(Date.now() / 1000)
  const endTs = Math.floor(nowInSeconds / HOUR_IN_SECONDS) * HOUR_IN_SECONDS
  const rangeInSeconds = parseSinceToSeconds(value)

  if (!rangeInSeconds) {
    return {
      startTs: null,
      endTs: null,
    }
  }

  return {
    startTs: endTs - rangeInSeconds,
    endTs,
  }
}

export function formatTimeLabel(ts) {
  return new Date(ts * 1000).toLocaleTimeString('hu-HU', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

export function formatDateTimeLabel(ts) {
  return new Date(ts * 1000).toLocaleString('hu-HU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}
