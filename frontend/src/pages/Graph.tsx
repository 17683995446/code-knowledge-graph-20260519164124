import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import * as d3 from 'd3';
import { ZoomIn, ZoomOut, Maximize2, Filter } from 'lucide-react';
import { graphApi, GraphNode, GraphLink } from '../api/client';

interface TooltipData {
  x: number;
  y: number;
  node: GraphNode;
}

export default function Graph() {
  const { projectId } = useParams<{ projectId: string }>();
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<TooltipData | null>(null);
  const [filters, setFilters] = useState({
    types: true,
    functions: true,
    call: true,
    inherit: true,
  });

  useEffect(() => {
    loadGraph();
  }, [projectId]);

  useEffect(() => {
    if (graphData.nodes.length > 0 && svgRef.current) {
      renderGraph();
    }
  }, [graphData, filters]);

  const loadGraph = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const data = await graphApi.getGraph(parseInt(projectId));
      setGraphData(data);
    } catch (error) {
      console.error('Failed to load graph:', error);
    }
    setLoading(false);
  };

  const renderGraph = () => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const filteredNodes = graphData.nodes.filter(node => {
      if (node.type === 'type' && !filters.types) return false;
      if (node.type === 'function' && !filters.functions) return false;
      return true;
    });

    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));

    const filteredLinks = graphData.links.filter(link => {
      if (!filteredNodeIds.has(link.source as string) || !filteredNodeIds.has(link.target as string)) {
        return false;
      }
      if (link.relation === 'call' && !filters.call) return false;
      if (['inherit', 'implement', 'import'].includes(link.relation) && !filters.inherit) return false;
      return true;
    });

    const g = svg.append('g');

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    const simulation = d3.forceSimulation(filteredNodes as any)
      .force('link', d3.forceLink(filteredLinks)
        .id((d: any) => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    const link = g.append('g')
      .selectAll('line')
      .data(filteredLinks)
      .join('line')
      .attr('stroke', (d: any) => {
        if (d.relation === 'call') return '#00d4ff';
        if (d.relation === 'inherit') return '#8b5cf6';
        if (d.relation === 'import') return '#00ff88';
        return '#666';
      })
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    const node = g.append('g')
      .selectAll('g')
      .data(filteredNodes)
      .join('g')
      .attr('class', 'graph-node')
      .call(d3.drag<SVGGElement, GraphNode>()
        .on('start', (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as any);

    node.append('circle')
      .attr('r', (d: GraphNode) => d.type === 'type' ? 20 : 15)
      .attr('fill', (d: GraphNode) => {
        if (d.type === 'type') {
          if (d.kind === 'class') return '#8b5cf6';
          if (d.kind === 'interface') return '#00d4ff';
          if (d.kind === 'struct') return '#f59e0b';
          return '#8b5cf6';
        }
        return '#00ff88';
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('filter', 'drop-shadow(0 0 10px currentColor)');

    node.append('text')
      .text((d: GraphNode) => d.name.length > 15 ? d.name.substring(0, 15) + '...' : d.name)
      .attr('x', 0)
      .attr('y', (d: GraphNode) => d.type === 'type' ? 35 : 28)
      .attr('text-anchor', 'middle')
      .attr('fill', '#e4e4e7')
      .attr('font-size', '11px')
      .attr('font-family', 'JetBrains Mono, monospace');

    node.on('click', (event: MouseEvent, d: GraphNode) => {
      const rect = svgRef.current?.getBoundingClientRect();
      if (rect) {
        setSelectedNode({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
          node: d,
        });
      }
    });

    node.on('mouseover', function() {
      d3.select(this).select('circle')
        .transition()
        .duration(200)
        .attr('r', function(d: any) { return d.type === 'type' ? 25 : 20; });
    });

    node.on('mouseout', function() {
      d3.select(this).select('circle')
        .transition()
        .duration(200)
        .attr('r', function(d: any) { return d.type === 'type' ? 20 : 15; });
    });

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });
  };

  const handleZoomIn = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
      1.3
    );
  };

  const handleZoomOut = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
      0.7
    );
  };

  const handleFitView = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.transition().call(
      d3.zoom<SVGSVGElement, unknown>().transform as any,
      d3.zoomIdentity
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-tech-blue border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">正在加载图谱数据...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-tech-blue/20 flex items-center justify-between">
        <h2 className="font-orbitron text-2xl font-bold text-tech-blue neon-text">
          知识图谱
        </h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm">
            <Filter className="w-4 h-4 text-gray-400" />
            <label className="flex items-center gap-1 text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.types}
                onChange={e => setFilters({ ...filters, types: e.target.checked })}
                className="rounded"
              />
              类型
            </label>
            <label className="flex items-center gap-1 text-gray-300 cursor-pointer ml-3">
              <input
                type="checkbox"
                checked={filters.functions}
                onChange={e => setFilters({ ...filters, functions: e.target.checked })}
                className="rounded"
              />
              函数
            </label>
          </div>
          <div className="flex gap-2">
            <button onClick={handleZoomIn} className="p-2 hover:bg-tech-blue/20 rounded-lg transition-colors">
              <ZoomIn className="w-5 h-5 text-tech-blue" />
            </button>
            <button onClick={handleZoomOut} className="p-2 hover:bg-tech-blue/20 rounded-lg transition-colors">
              <ZoomOut className="w-5 h-5 text-tech-blue" />
            </button>
            <button onClick={handleFitView} className="p-2 hover:bg-tech-blue/20 rounded-lg transition-colors">
              <Maximize2 className="w-5 h-5 text-tech-blue" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 relative bg-space-dark/50">
        <svg ref={svgRef} className="w-full h-full" />

        {selectedNode && (
          <div
            className="tooltip"
            style={{
              left: selectedNode.x + 20,
              top: selectedNode.y - 20,
            }}
          >
            <div className="font-bold text-tech-blue mb-1">{selectedNode.node.name}</div>
            <div className="text-xs text-gray-400">
              类型: {selectedNode.node.type} ({selectedNode.node.kind})
            </div>
            <div className="text-xs text-gray-400 mt-1">
              文件: {selectedNode.node.file_path}
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="absolute top-2 right-2 text-gray-500 hover:text-white"
            >
              ×
            </button>
          </div>
        )}

        <div className="absolute bottom-4 left-4 glass-card p-4 text-xs">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-quantum-purple"></div>
              <span className="text-gray-400">类</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-tech-blue"></div>
              <span className="text-gray-400">接口</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-neon-green"></div>
              <span className="text-gray-400">函数</span>
            </div>
          </div>
        </div>

        <div className="absolute bottom-4 right-4 glass-card p-4 text-xs">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-tech-blue"></div>
              <span className="text-gray-400">调用</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-quantum-purple"></div>
              <span className="text-gray-400">继承</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-neon-green"></div>
              <span className="text-gray-400">导入</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
