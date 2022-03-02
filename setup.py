from logging.config import dictConfig

from organization import create_app
from config import LoggerConfig, Config


# Logger configuration setup
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': LoggerConfig.format,
        'datefmt': LoggerConfig.datefmt,
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'fileHandlerLog': {
            'class': 'logging.FileHandler',
            'filename': LoggerConfig.filename,
            'formatter': 'default'
        }
    },
    'root': {
        'level': LoggerConfig.level,
        'handlers': ['wsgi', 'fileHandlerLog']
    }
})


app = create_app()

if __name__ == '__main__':
    app.logger.info("App started...")
    app.run(host=Config.HOST, port=int(Config.PORT))
    app.logger.warning("App Stopped.")
