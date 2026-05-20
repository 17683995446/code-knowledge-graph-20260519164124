# 子模块1 - 数据处理
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import json

@dataclass
class DataRecord:
    """数据记录"""
    id: int
    value: str
    metadata: Dict[str, Any]

class DataProcessor:
    """数据处理器"""
    def __init__(self):
        self._records = []

    def add_record(self, record: DataRecord):
        """添加记录"""
        self._records.append(record)

    def get_records(self) -> List[DataRecord]:
        """获取所有记录"""
        return self._records

    def filter_records(self, predicate) -> List[DataRecord]:
        """过滤记录"""
        return [r for r in self._records if predicate(r)]

class DataExporter:
    """数据导出器"""
    @staticmethod
    def to_json(records: List[DataRecord]) -> str:
        """导出为JSON"""
        return json.dumps([{
            'id': r.id,
            'value': r.value,
            'metadata': r.metadata
        } for r in records], indent=2)

    @staticmethod
    def to_csv(records: List[DataRecord]) -> str:
        """导出为CSV"""
        lines = ["id,value"]
        for r in records:
            lines.append(f"{r.id},{r.value}")
        return "\n".join(lines)

def process_data(data: List[Dict[str, Any]]) -> List[DataRecord]:
    """处理数据函数"""
    return [
        DataRecord(
            id=d['id'],
            value=d['value'],
            metadata=d.get('metadata', {})
        )
        for d in data
    ]
