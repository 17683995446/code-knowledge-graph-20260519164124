import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export interface Project {
  id: number;
  name: string;
  path: string;
  created_at: number;
  updated_at: number;
}

export interface Stats {
  file_count: number;
  type_count: number;
  function_count: number;
  languages: Record<string, number>;
}

export interface GraphNode {
  id: string;
  name: string;
  type: 'type' | 'function';
  kind: string;
  file_id: number;
  file_path: string;
  type_id?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  relation: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface SearchResult {
  id: number;
  name: string;
  kind: string;
  file_path: string;
  entity_type: string;
}

export interface ChatMessage {
  role: string;
  content: string;
}

export const projectsApi = {
  getAll: () => api.get<Project[]>('/projects').then(res => res.data),
  create: (data: { name: string; path: string }) => api.post<Project>('/projects', data).then(res => res.data),
  delete: (id: number) => api.delete(`/projects/${id}`),
  sync: (id: number) => api.post(`/projects/${id}/sync`).then(res => res.data),
  getStats: (id: number) => api.get<Stats>(`/projects/${id}/stats`).then(res => res.data),
};

export const graphApi = {
  getGraph: (projectId: number) => api.get<GraphData>(`/graph/${projectId}`).then(res => res.data),
  search: (projectId: number, query: string, typeFilter?: string) =>
    api.get<SearchResult[]>('/search', {
      params: { project_id: projectId, query, type_filter: typeFilter }
    }).then(res => res.data),
};

export const chatApi = {
  sendMessage: (projectId: number, message: string, history: ChatMessage[]) =>
    api.post('/chat', {
      project_id: projectId,
      message,
      history,
    }).then(res => res.data),
};

export default api;
