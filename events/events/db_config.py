from .settings import BASE_DIR

DB_CONFIG_POSTGRESQL = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'barrqom7nnxy7tw1sgzk',
        'USER': 'umkinxclbpuf8mgxrq8a',
        'PASSWORD': 'G958L4UxOwNFHShrIrGnNwA6vhGo2W',
        'HOST': 'barrqom7nnxy7tw1sgzk-postgresql.services.clever-cloud.com',
        'PORT': '50013',
    }

DB_CONFIG_POSTGRESQL_HOME = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'meetings_db',
        'USER': 'meetings',
        'PASSWORD': 'meetings',
        'HOST': 'localhost',
        'PORT': '5432',
    }

DB_CONFIG_MYSQL = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bcuxr2z3vgwgxr4vkvhr',
        'USER': 'uox6clz9p9fjkpsr',
        'PASSWORD': 'Fn0hF8Vgc6UYQ8VKegrU',
        'HOST': 'bcuxr2z3vgwgxr4vkvhr-mysql.services.clever-cloud.com',
        'PORT': '3306',
    }

DB_SQLITE = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
