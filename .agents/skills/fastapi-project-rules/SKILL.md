---
name: fastapi-project-rules
description: "新建 FastAPI 项目骨架、在既有 FastAPI 项目中新增或修改接口、编写 controller 与 service 与 dao 与 schema 与 client 分层代码、装配 app 与 CORS 与全局异常处理器、组织路由与依赖注入与数据库会话、审查 FastAPI 目录结构与分层实现时触发。"
disable-model-invocation: false
---

# FastAPI 项目编码规则

以下规则为强制约束，逐条执行。

## 目录与分层

1. 新建项目时，应用入口只用工作区根目录的 `main.py`，业务代码全部放进 `src/`。

2. `src/` 下只建 `controller`、`service`、`dao`、`model`、`schema`、`core`、`client`、`util` 八个包，包内按业务域拆模块文件。

3. 模块文件名用「业务域 + 层名」的小写下划线形式。

   > 示例：`user_controller.py`、`user_service.py`、`user_dao.py`、`user_model.py`。

4. 调用方向只允许 `controller → service → dao / client / util`；禁止下层模块反向导入上层模块。

5. `controller` 需要数据时，在对应 Service 上补一个方法转发；禁止 `controller` 导入并调用 DAO。

6. `model` 只放 SQLAlchemy ORM 映射类，`schema` 只放 Pydantic 模型；禁止一个类同时承担持久化映射与请求响应校验。

7. `core` 只放常量、异常类、配置类与全局异常处理器这类无业务语义的基础设施代码。

8. 只有用户明确要求按子应用拆分时才建 `src/subapp/`；未提出时禁止创建该目录。

9. 建 `src/subapp/<app_name>/` 时在其内部复刻主 app 的分层目录，且禁止在子应用内再嵌套 `subapp`。

## 配置

10. 配置值只从工作区根目录的 `.env` 读取；禁止在业务模块中调用 `os.getenv` 或另建配置文件。

11. 全局配置用一个继承 `BaseSettings` 的类表达，每个字段声明类型与默认值，并用 `model_config = SettingsConfigDict(env_file=".env")` 绑定文件。

12. 配置类所在文件末尾必须实例化一个模块级单例，用到配置的模块导入该单例并直接读属性。

    > 示例：
    > ```python
    > settings = Settings()                        # 配置文件末尾
    > timeout = settings.redis_timeout_seconds     # 用
    > timeout = Settings().redis_timeout_seconds   # 禁止：每次重新解析 .env
    > ```

13. 配置只以导入单例的方式获取；禁止把配置对象做成 `Depends` 依赖或逐层当参数传递。

14. 凭据只写进 `.env`，同时在 `.env.example` 补同名空值键与一行用途注释，并确认 `.gitignore` 已忽略 `.env`。

15. 禁止在 FastAPI 实例的 `app.state` 上挂载任何属性；客户端、配置与共享对象改由各自模块的单例持有。

## 应用装配

16. `main.py` 只做四件事：实例化 `FastAPI`、注册中间件、注册路由、注册异常处理器；禁止在其中写端点与业务逻辑。

17. 路由只用 `app.include_router()` 挂载 `src/controller/router.py` 汇总出的总路由。

18. 必须显式注册 `CORSMiddleware`，`allow_origins`、`allow_methods`、`allow_headers` 逐项从配置单例读取；禁止硬编码 `["*"]`。

19. 进程启停时需要初始化或释放的资源用 `lifespan` 异步上下文管理器处理；禁止用已废弃的 `@app.on_event`。

20. `lifespan` 中只调用各 client 模块自身的初始化与关闭函数；禁止在其中构造对象再挂到 `app` 上。

## Controller 与路由

21. 每个 controller 模块必须在模块级定义 `router = APIRouter(prefix=..., tags=[...])`；禁止把 `APIRouter` 放进类属性或实例属性。

22. 同一业务域的端点必须收进一个以该业务域命名的 Controller 类，该类只作命名空间。

23. 端点方法一律用 `@staticmethod`，且 `@staticmethod` 写在 `@router.<method>` 上方。

    > 示例：
    > ```python
    > @staticmethod                              # 用
    > @router.get("/{user_id}")
    > async def get_user(user_id: int) -> UserRead: ...
    >
    > @router.get("/{user_id}")                  # 禁止：装饰器顺序颠倒导致注册失败
    > @staticmethod
    > ```

24. 禁止实例化 Controller 类，禁止为它定义 `__init__`、实例属性与类属性依赖；数据库会话与用户校验等接口依赖用 `Depends` 注入。

25. 每个端点固定接收名为 `db_session` 的数据库会话依赖，类型别名统一命名为 `DBSessionDependency`；禁止用 `SessionDep` 等缩写。Controller 模块直接导入对应 Service，禁止把 Service 注册成 `Depends` 依赖。

    > 示例：
    > ```python
    > async def get_user(
    >     user_id: int,
    >     db_session: DBSessionDependency,
    > ) -> UserRead:
    >     return await UserService.get_user(db_session, user_id)
    > ```

26. Controller 只处理路径参数、查询参数、请求体、请求头、状态码与依赖注入，取到参数后立即转交 Service。

27. 端点函数体禁止出现业务条件分支、循环与 ORM 调用；这类逻辑下沉到 Service。

28. 端点一律用 `async def` 定义。

29. `src/controller/router.py` 只做汇总：建一个总 `APIRouter`，逐个 `include_router` 各业务 controller 的 `router`。

30. 统一 URL 前缀与版本号在 `router.py` 的总路由上用 `prefix` 声明；禁止在每个 controller 的 `prefix` 里重复拼接。

## Schema 与响应

31. 请求体与响应体一律用 `schema/` 下的 Pydantic 模型表达，按用途拆成 `XxxCreate`、`XxxUpdate`、`XxxRead`。

32. 每个端点必须用函数返回类型注解声明 `ResponseSchema[业务 Schema]` 响应模型；禁止改用装饰器的 `response_model` 参数。Service 只返回业务 Schema，由 Controller 负责包装统一响应。

33. 统一响应模型命名为 `ResponseSchema`，固定包含 `code: int`、`msg: str` 与泛型 `data`。普通端点直接返回该 Pydantic 模型并由 FastAPI 序列化；全局异常处理器也必须先构造 `ResponseSchema`，再以 Pydantic JSON 模式生成 `JSONResponse` 内容，保证嵌套 `datetime` 等对象可序列化。禁止自定义 `JSONResponse` 子类。

34. 禁止直接返回 ORM 对象；在 Service 中用 `XxxRead.model_validate(obj)` 转换后再返回。

35. 响应模型的 `code` 与实际 HTTP 状态码保持一致。非 `200` 的成功状态码用端点装饰器的 `status_code` 参数声明；禁止在函数体内手工构造 `Response` 改状态码。

36. Schema 类只允许字段定义与字段校验器；禁止在其中写业务方法与数据库访问。

## Service 与 DAO

37. 业务规则、流程编排与状态判定只写在 Service 中，Service 方法一律 `async def`。

38. Service 在模块顶部导入 DAO、client 与 util，并在业务方法中直接调用；Service 方法显式接收 `db_session` 与接口参数，禁止通过依赖提供函数构造 Service。

39. 数据库引擎、`async_sessionmaker` 与会话依赖函数只定义在 `src/client/` 的数据库模块中。

40. 会话依赖只提供带事务的一种，用 `async_sessionmaker.begin()` 产出会话并导出 `Annotated` 别名；禁止再提供不带事务的会话依赖。

    > 示例：
    > ```python
    > async def get_transaction_session() -> AsyncGenerator[AsyncSession, None]:
    >     async with async_session.begin() as db_session:
    >         yield db_session
    >
    > DBSessionDependency = Annotated[
    >     AsyncSession,
    >     Depends(get_transaction_session),
    > ]
    > ```

41. 会话在 Controller 端点中以 `db_session: DBSessionDependency` 注入，Controller 调用 Service 时显式向下传递；禁止在 Service 与 DAO 内部自行创建会话。

    > 示例：
    > ```python
    > async def get_user(
    >     user_id: int,
    >     db_session: DBSessionDependency,
    > ) -> UserRead:
    >     return await UserService.get_user(db_session, user_id)
    > ```

42. SQLAlchemy 语句的构造与执行只写在 DAO 中；需要访问数据库的 DAO 方法显式接收 `db_session` 与基本参数，不访问数据库的方法不强制接收会话。DAO 只返回 ORM 对象或标量。

43. 事务提交与回滚由会话依赖的 `begin()` 上下文统一处理；禁止在 DAO 与 Service 中调用 `session.commit()` 与 `session.rollback()`。

44. DAO 禁止导入 `schema` 与 `service`，也禁止返回 Pydantic 模型。

## Client 与 Util

45. 数据库、缓存、向量库与第三方 HTTP 服务的连接和调用一律封装在 `src/client/` 下，一个外部依赖一个模块。

46. client 对外暴露的方法只返回项目自己的数据结构；禁止让调用方感知第三方 SDK 的模型类型与异常类型。

47. `util/` 只放与业务无关的纯函数和数据结构转换；禁止在其中访问数据库、发起网络请求与读取配置单例。

## 异常与日志

48. 业务异常类统一定义在 `src/core/` 的异常模块中，名称以 `Exception` 结尾并继承同一个项目基类异常。基础异常统一携带 `code: int`、`message: str` 与默认为空字典的 `data`；HTTP 响应需要状态码时直接使用 `code`。

    常用错误类别的 `code` 定义为 `src/core/constants.py` 中的整数常量并复用；禁止为每种细微情况新增错误码。

49. DAO 捕获 `SQLAlchemyError`、client 捕获第三方 SDK 异常后，必须转换成项目异常并用 `raise ... from exc` 向上抛出。

50. Service 只负责抛出业务异常与为底层异常补充业务上下文；禁止吞掉异常后返回 `None` 或默认值。

51. Controller 禁止用 `try/except` 捕获业务异常，也禁止手工转换成 `HTTPException`；异常一律抛给全局异常处理器。

52. 全局异常处理器在 `src/core/` 中定义并在 `main.py` 注册，它是 HTTP 链路唯一记录异常日志的位置。项目异常、HTTP 异常、请求字段校验异常与未知异常都使用 `ResponseSchema` 响应；请求字段校验响应只暴露字段位置、原因与错误类型，禁止回传原始输入值。

53. 未知异常用 `logger.exception` 记 `ERROR`；已定义的业务异常按业务语义记 `INFO` 或 `WARNING`，禁止一律记成 `ERROR`。

54. 同一异常调用链只允许记录一次异常日志；DAO、client、Service、Controller 中禁止出现 `logger.error` 与 `logger.exception`。

    > 示例：
    > ```python
    > except SQLAlchemyError as exc:
    >     logger.exception("query user failed")              # 禁止：边界会再记一次
    >     raise DatabaseException(
    >         code=SERVICE_UNAVAILABLE_CODE,
    >         message="query user failed",
    >     ) from exc                                           # 用
    > ```

55. 正常日志只在 Service 中按有业务价值的事件记 `INFO`；禁止记录方法进出、每次查询成功与局部变量状态。

56. 日志上下文一律用 `extra` 传结构化字段，禁止用 f-string 拼接；禁止写入密钥、令牌与完整敏感请求体。

    > 示例：
    > ```python
    > logger.info(f"user {user_id} created")                    # 禁止
    > logger.info("user created", extra={"user_id": user_id})   # 用
    > ```

57. 访问日志用一个中间件统一记录 `method`、`path`、`status_code`、`duration_ms`；禁止在端点内逐个记录请求信息。
