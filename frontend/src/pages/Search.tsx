import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Search as SearchIcon, Filter, FileCode, Layers, Zap } from 'lucide-react';
import { graphApi, SearchResult } from '../api/client';

export default function Search() {
  const { projectId } = useParams<{ projectId: string }>();
  const [query, setQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    if (query.length >= 2 && projectId) {
      performSearch();
    } else {
      setResults([]);
      setHasSearched(false);
    }
  }, [query, typeFilter, projectId]);

  const performSearch = async () => {
    if (!projectId || query.length < 2) return;

    setLoading(true);
    setHasSearched(true);
    try {
      const data = await graphApi.search(parseInt(projectId), query, typeFilter || undefined);
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
    }
    setLoading(false);
  };

  const getIcon = (entityType: string) => {
    switch (entityType) {
      case 'type':
        return Layers;
      case 'function':
        return Zap;
      default:
        return FileCode;
    }
  };

  const getColor = (entityType: string) => {
    switch (entityType) {
      case 'type':
        return 'text-quantum-purple';
      case 'function':
        return 'text-neon-green';
      default:
        return 'text-tech-blue';
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="font-orbitron text-3xl font-bold text-tech-blue neon-text mb-2">
          搜索
        </h2>
        <p className="text-gray-400">在代码库中搜索类型、函数和其他实体</p>
      </div>

      <div className="glass-card p-6 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="输入搜索关键词..."
              className="input-glow w-full pl-12"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={typeFilter}
              onChange={e => setTypeFilter(e.target.value)}
              className="input-glow"
            >
              <option value="">全部</option>
              <option value="type">类型</option>
              <option value="function">函数</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="w-12 h-12 border-4 border-tech-blue border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">搜索中...</p>
        </div>
      ) : hasSearched && results.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <SearchIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl text-gray-300 mb-2">未找到结果</h3>
          <p className="text-gray-500">尝试使用不同的关键词或筛选条件</p>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-4">
          <div className="text-sm text-gray-400 mb-4">
            找到 {results.length} 个结果
          </div>
          {results.map((result, index) => {
            const Icon = getIcon(result.entity_type);
            return (
              <div
                key={`${result.entity_type}-${result.id}-${index}`}
                className="glass-card p-4 hover:shadow-lg hover:shadow-tech-blue/20 transition-all duration-200 cursor-pointer"
              >
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-lg bg-space-dark ${getColor(result.entity_type)}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg text-white">{result.name}</h3>
                      <span className={`px-2 py-1 rounded text-xs ${getColor(result.entity_type)} bg-current/10`}>
                        {result.kind}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <FileCode className="w-4 h-4" />
                      <span>{result.file_path}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="glass-card p-12 text-center">
          <SearchIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl text-gray-300 mb-2">开始搜索</h3>
          <p className="text-gray-500">输入至少2个字符来搜索代码实体</p>
        </div>
      )}
    </div>
  );
}
