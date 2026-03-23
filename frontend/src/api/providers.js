import service, { requestWithRetry } from './index'

export function validateProvider(data) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/providers/validate',
      method: 'post',
      data
    })
  )
}

export function refineBrief(data) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/providers/refine-brief',
      method: 'post',
      data
    })
  )
}

export function saveProjectProviderConfig(projectId, data) {
  return requestWithRetry(() =>
    service({
      url: `/api/graph/project/${projectId}/llm-config`,
      method: 'post',
      data
    })
  )
}
