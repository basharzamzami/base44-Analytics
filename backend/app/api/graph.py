from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.user import User
from app.services.graph_service import graph_service
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


class GraphQueryRequest(BaseModel):
    query: str
    vertical: Optional[str] = None


class GraphQueryResponse(BaseModel):
    success: bool
    results: list
    count: int
    query_type: str
    error: Optional[str] = None


@router.post("/query", response_model=GraphQueryResponse)
async def query_graph(
    request: GraphQueryRequest,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Query the graph with natural language or Cypher"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    try:
        result = graph_service.query_graph(
            tenant_id=int(x_tenant_id),
            query=request.query,
            vertical=request.vertical
        )
        
        return GraphQueryResponse(
            success=result["success"],
            results=result["results"],
            count=result["count"],
            query_type=result.get("query_type", "general"),
            error=result.get("error")
        )
        
    except Exception as e:
        return GraphQueryResponse(
            success=False,
            results=[],
            count=0,
            query_type="error",
            error=str(e)
        )


@router.get("/statistics")
async def get_graph_statistics(
    vertical: Optional[str] = None,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get graph statistics"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    try:
        stats = graph_service.get_graph_statistics(
            tenant_id=int(x_tenant_id),
            vertical=vertical
        )
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph statistics: {str(e)}"
        )


@router.get("/nodes")
async def get_graph_nodes(
    node_type: Optional[str] = None,
    limit: int = 100,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get graph nodes"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    try:
        # For demo purposes, return mock nodes
        mock_data = graph_service.mock_graph_data.get("marketing_agency", {"nodes": []})
        
        nodes = mock_data["nodes"]
        if node_type:
            nodes = [node for node in nodes if node.get("type") == node_type]
        
        return {
            "success": True,
            "nodes": nodes[:limit],
            "count": len(nodes[:limit])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph nodes: {str(e)}"
        )


@router.get("/edges")
async def get_graph_edges(
    rel_type: Optional[str] = None,
    limit: int = 100,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get graph edges"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    try:
        # For demo purposes, return mock edges
        mock_data = graph_service.mock_graph_data.get("marketing_agency", {"edges": []})
        
        edges = mock_data["edges"]
        if rel_type:
            edges = [edge for edge in edges if edge.get("type") == rel_type]
        
        return {
            "success": True,
            "edges": edges[:limit],
            "count": len(edges[:limit])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph edges: {str(e)}"
        )

