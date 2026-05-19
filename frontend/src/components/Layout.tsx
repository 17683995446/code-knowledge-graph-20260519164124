import { Outlet, useLocation, useParams } from 'react-router-dom';
import { Home, Network, MessageCircle, Search, Atom } from 'lucide-react';

export default function Layout() {
  const location = useLocation();
  const params = useParams();

  const getNavItems = () => {
    const projectId = params.projectId;
    if (!projectId) {
      return [
        { path: '/', icon: Home, label: '项目列表', active: location.pathname === '/' },
      ];
    }

    return [
      { path: '/', icon: Home, label: '项目列表', active: location.pathname === '/' },
      { path: `/graph/${projectId}`, icon: Network, label: '知识图谱', active: location.pathname.startsWith('/graph') },
      { path: `/search/${projectId}`, icon: Search, label: '搜索', active: location.pathname.startsWith('/search') },
      { path: `/chat/${projectId}`, icon: MessageCircle, label: 'AI问答', active: location.pathname.startsWith('/chat') },
    ];
  };

  const navItems = getNavItems();

  return (
    <div className="flex h-screen bg-space-dark">
      <aside className="sidebar">
        <div className="p-6 border-b border-tech-blue/20">
          <div className="flex items-center gap-3">
            <Atom className="w-8 h-8 text-tech-blue neon-text" />
            <h1 className="font-orbitron text-xl font-bold text-tech-blue neon-text">
              CodeGraph
            </h1>
          </div>
          <p className="text-xs text-gray-500 mt-2">全编程语言代码知识图谱</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <div
              key={item.path}
              className={`nav-item ${item.active ? 'active' : ''}`}
              onClick={() => window.location.href = item.path}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </div>
          ))}
        </nav>

        <div className="p-4 border-t border-tech-blue/20">
          <div className="glass-card p-4">
            <div className="text-xs text-gray-400">系统状态</div>
            <div className="flex items-center gap-2 mt-2">
              <div className="w-2 h-2 rounded-full bg-neon-green pulse-glow"></div>
              <span className="text-sm text-neon-green">运行中</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
