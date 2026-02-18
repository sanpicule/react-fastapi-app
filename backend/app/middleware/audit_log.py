import json
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from app.db.session import AsyncSessionLocal
from app.models.audit_log import AuditLog


class AuditLogMiddleware(BaseHTTPMiddleware):
    # 除外するパス
    EXCLUDED_PATHS = {
        "/docs",
        "/redoc",
        "/openapi.json",
    }
    
    async def dispatch(self, request: Request, call_next):
        # 除外パスのチェック
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # リクエストボディの読み取り
        request_body = None
        if request.method in ["POST", "PUT", "POST", "DELETE"]:
            body = await request.body()
            if body:
                try:
                    request_body = body.decode("utf-8")
                except Exception:
                    request_body = str(body)
            
            # ボディを再利用できるように設定
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive

        # レスポンスの取得
        response = await call_next(request)
        
        # レスポンスボディの読み取り
        response_body = None
        response_body_bytes = b""
        
        if isinstance(response, StreamingResponse):
            # StreamingResponseの場合、body_iteratorを読み取る
            async for chunk in response.body_iterator:
                response_body_bytes += chunk
            
            if response_body_bytes:
                try:
                    response_body = response_body_bytes.decode("utf-8")
                except Exception:
                    response_body = str(response_body_bytes)
            
            # 新しいレスポンスを作成
            new_response = Response(
                content=response_body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        else:
            # 通常のResponseの場合
            new_response = response
            if hasattr(response, 'body'):
                response_body_bytes = response.body
                try:
                    response_body = response_body_bytes.decode("utf-8")
                except Exception:
                    response_body = str(response_body_bytes)
        
        # 監査ログの記録
        try:
            async with AsyncSessionLocal() as session:
                audit_log = AuditLog(
                    user_id=None,  # 認証実装後にユーザーIDを設定
                    action=f"{request.method} {request.url.path}",
                    resource_type=self._extract_resource_type(request.url.path),
                    resource_id=self._extract_resource_ids(request.path_params),
                    details=json.dumps({
                        "query_params": dict(request.query_params),
                        "path_params": dict(request.path_params),
                    }) if request.query_params or request.path_params else None,
                    request_body=request_body,
                    response_body=response_body,
                    ip_address=self._get_client_ip(request),
                    created_at=datetime.utcnow(),
                )
                session.add(audit_log)
                await session.commit()
        except Exception as e:
            # ログ記録失敗してもレスポンスは返す
            print(f"Failed to log audit: {e}")
        
        return new_response
    
    def _extract_resource_type(self, path: str) -> str | None:
        """パスからリソースタイプを抽出"""
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 3:
            return parts[2]  # /api/v1/users -> users
        return None
    
    def _extract_resource_ids(self, path_params: dict) -> int | None:
        """パスパラメータから最後のリソースIDを抽出"""
        if not path_params:
            return None
        
        # ID系のパラメータのみを抽出
        id_params = []
        for key, value in path_params.items():
            # IDっぽいパラメータを収集
            if key == "id" or key.endswith("_id"):
                try:
                    # 整数変換できる場合のみ追加
                    id_params.append(int(value))
                except (ValueError, TypeError):
                    pass
        
        if not id_params:
            return None
        
        # 最後のIDを返す
        return id_params[-1]
    
    def _get_client_ip(self, request: Request) -> str | None:
        """クライアントIPアドレスを取得"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else None
