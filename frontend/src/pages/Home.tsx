import { useState, useEffect } from 'react';
import { Plus, Trash2, RefreshCw, Folder, FileCode, Layers, Zap } from 'lucide-react';
import { projectsApi, Project, Stats } from '../api/client';

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<Record<number, Stats>>({});
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', path: '' });
  const [syncing, setSyncing] = useState<number | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await projectsApi.getAll();
      setProjects(data);

      const statsMap: Record<number, Stats> = {};
      for (const project of data) {
        try {
          statsMap[project.id] = await projectsApi.getStats(project.id);
        } catch {
          statsMap[project.id] = {
            file_count: 0,
            type_count: 0,
            function_count: 0,
            languages: {}
          };
        }
      }
      setStats(statsMap);
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

  const handleAddProject = async () => {
    if (!newProject.name || !newProject.path) return;

    try {
      const project = await projectsApi.create(newProject);
      setProjects([project, ...projects]);
      setShowAddModal(false);
      setNewProject({ name: '', path: '' });

      const projectStats = await projectsApi.getStats(project.id);
      setStats({ ...stats, [project.id]: projectStats });
    } catch (error) {
      console.error('Failed to add project:', error);
    }
  };

  const handleDeleteProject = async (id: number) => {
    if (!confirm('确定要删除这个项目吗？')) return;

    try {
      await projectsApi.delete(id);
      setProjects(projects.filter(p => p.id !== id));
      const newStats = { ...stats };
      delete newStats[id];
      setStats(newStats);
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  const handleSync = async (id: number) => {
    setSyncing(id);
    try {
      await projectsApi.sync(id);
      const projectStats = await projectsApi.getStats(id);
      setStats({ ...stats, [id]: projectStats });
    } catch (error) {
      console.error('Failed to sync project:', error);
    }
    setSyncing(null);
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="font-orbitron text-3xl font-bold text-tech-blue neon-text mb-2">
            项目管理
          </h2>
          <p className="text-gray-400">管理和分析您的代码项目</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="glow-button flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          添加项目
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Folder className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl text-gray-300 mb-2">暂无项目</h3>
          <p className="text-gray-500 mb-6">点击上方按钮添加您的第一个项目</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="glow-button"
          >
            添加项目
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {projects.map(project => {
            const projectStats = stats[project.id] || {
              file_count: 0,
              type_count: 0,
              function_count: 0,
              languages: {}
            };

            return (
              <div key={project.id} className="glass-card p-6 hover:shadow-xl hover:shadow-tech-blue/20 transition-all duration-300">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-tech-blue to-quantum-purple flex items-center justify-center">
                      <FileCode className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg text-white">{project.name}</h3>
                      <p className="text-xs text-gray-500 truncate max-w-[200px]">{project.path}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSync(project.id)}
                      disabled={syncing === project.id}
                      className="p-2 hover:bg-tech-blue/20 rounded-lg transition-colors"
                      title="同步项目"
                    >
                      <RefreshCw className={`w-4 h-4 text-tech-blue ${syncing === project.id ? 'animate-spin' : ''}`} />
                    </button>
                    <button
                      onClick={() => handleDeleteProject(project.id)}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                      title="删除项目"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-space-dark/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                      <FileCode className="w-3 h-3" />
                      文件数
                    </div>
                    <div className="text-2xl font-bold text-white">{projectStats.file_count}</div>
                  </div>
                  <div className="bg-space-dark/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                      <Layers className="w-3 h-3" />
                      类型数
                    </div>
                    <div className="text-2xl font-bold text-quantum-purple">{projectStats.type_count}</div>
                  </div>
                  <div className="bg-space-dark/50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
                      <Zap className="w-3 h-3" />
                      函数数
                    </div>
                    <div className="text-2xl font-bold text-neon-green">{projectStats.function_count}</div>
                  </div>
                  <div className="bg-space-dark/50 rounded-lg p-3">
                    <div className="text-gray-400 text-xs mb-1">语言</div>
                    <div className="text-lg font-bold text-tech-blue">
                      {Object.keys(projectStats.languages).length}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => window.location.href = `/graph/${project.id}`}
                    className="flex-1 py-2 bg-tech-blue/20 hover:bg-tech-blue/30 text-tech-blue rounded-lg text-sm transition-colors"
                  >
                    查看图谱
                  </button>
                  <button
                    onClick={() => window.location.href = `/search/${project.id}`}
                    className="flex-1 py-2 bg-quantum-purple/20 hover:bg-quantum-purple/30 text-quantum-purple rounded-lg text-sm transition-colors"
                  >
                    搜索
                  </button>
                  <button
                    onClick={() => window.location.href = `/chat/${project.id}`}
                    className="flex-1 py-2 bg-neon-green/20 hover:bg-neon-green/30 text-neon-green rounded-lg text-sm transition-colors"
                  >
                    AI问答
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="glass-card p-8 w-full max-w-md">
            <h3 className="font-orbitron text-xl font-bold text-tech-blue mb-6">添加新项目</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">项目名称</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={e => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="例如：我的项目"
                  className="input-glow w-full"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">项目路径</label>
                <input
                  type="text"
                  value={newProject.path}
                  onChange={e => setNewProject({ ...newProject, path: e.target.value })}
                  placeholder="/path/to/your/project"
                  className="input-glow w-full"
                />
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 py-2 border border-gray-600 hover:border-gray-500 text-gray-300 rounded-lg transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleAddProject}
                className="flex-1 glow-button"
                disabled={!newProject.name || !newProject.path}
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
