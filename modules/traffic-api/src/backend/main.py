import uvicorn
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from .utils import log
from .routes.base import router
from . import conf

log.init(conf.get_log_level())
logger = log.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize PostgreSQL client if enabled
    if conf.USE_POSTGRES:
        from .clients.postgres import PostgresClient
        from sqlmodel import SQLModel
        # Import models to register them with SQLModel
        from .db import models  # noqa: F401

        postgres_config = conf.get_postgres_conf()
        pool_config = conf.get_postgres_pool_conf()
        app.state.postgres_client = PostgresClient(postgres_config, pool_config)
        await app.state.postgres_client.initialize()
        await app.state.postgres_client.init_connection()

        # Create tables after connection is established
        await app.state.postgres_client.create_tables(SQLModel.metadata)

    # Initialize Couchbase client if enabled
    if conf.USE_COUCHBASE:
        from .clients.couchbase import CouchbaseClient
        couchbase_config = conf.get_couchbase_conf()
        app.state.couchbase_client = CouchbaseClient(couchbase_config)
        await app.state.couchbase_client.init_connection()

        # Import and initialize all Couchbase collections
        from .couchbase.collections import COLLECTIONS
        for Collection in COLLECTIONS:
            await Collection(app.state.couchbase_client).initialize()


    # Initialize auth client if enabled
    if conf.USE_AUTH:
        from .utils import auth
        app.state.auth_client = auth.AuthClient(conf.get_auth_config())
    else:
        logger.warning("Authentication is disabled (set USE_AUTH to enable)")

    # Initialize Temporal client if enabled
    if conf.USE_TEMPORAL:
        from .clients.temporal import TemporalClient
        from .workflows import WORKFLOWS, ACTIVITIES
        temporal_config = conf.get_temporal_conf()
        app.state.temporal_client = TemporalClient(
            config=temporal_config,
            workflows=WORKFLOWS,
            activities=ACTIVITIES
        )
        await app.state.temporal_client.initialize()

    # Initialize Twilio client if enabled
    if conf.USE_TWILIO:
        from .clients.twilio import TwilioClient
        twilio_config = conf.get_twilio_conf()
        app.state.twilio_client = TwilioClient(twilio_config)
        await app.state.twilio_client.initialize()
        await app.state.twilio_client.init_connection()

    yield

    # Clean up PostgreSQL client if enabled
    if conf.USE_POSTGRES:
        await app.state.postgres_client.close()

    # Clean up Couchbase client if enabled
    if conf.USE_COUCHBASE:
        await app.state.couchbase_client.close()

    # Clean up Temporal client if enabled
    if conf.USE_TEMPORAL:
        await app.state.temporal_client.close()

    # Clean up Twilio client if enabled
    if conf.USE_TWILIO:
        await app.state.twilio_client.close()

app = FastAPI(
    title="Backend API",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan,
    debug=conf.get_http_expose_errors(),
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main() -> None:
    if not conf.validate():
        raise ValueError("Invalid configuration.")

    http_conf = conf.get_http_conf()
    logger.info(f"Starting API on port {http_conf.port}")
    uvicorn.run(
        "backend.main:app",
        host=http_conf.host,
        port=http_conf.port,
        reload=http_conf.autoreload,
        log_level="info",
        log_config=None
    )
