# README

Se pretende realizar una aplicacion 12factor

## Preparacion entorno

1. Tener las siguientes dependencias instaladas

  ```
  sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
  libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl
  ```

2. Instalar pyenv

  ```bash
  curl https://pyenv.run | bash
  ```

3. Anadir a .zshrc

  ```bash
  export PATH="$HOME/.pyenv/bin:$PATH"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
  ```

4. Reiniciar el shell.

5. Instalar la version de python deseada (3.7.2)

  ```bash
  pyenv install -v 3.7.2
  ```

6. Crear directorio del proyecto, generar virtualenv y activarlo

  ```bash
  mkdir flask_keyforge
  cd flask_keyforge
  pyenv virtualenv 3.7.2 flask_keyforge
  pyenv local flask_keyforge
  ```

7. Generar base de datos. Abrir terminal python y ejecutar

```python
import app; app.create_ddbb()
```

## Fuentes

* [intro-to-pyenv](https://realpython.com/intro-to-pyenv/)


# TODO

https://keyforge-compendium.com/cards?utf8=%E2%9C%93&filterrific%5Bsearch_title%5D=&filterrific%5Bsearch_text%5D=&filterrific%5Bwith_traits%5D=&filterrific%5Bwith_power%5D=&filterrific%5Bwith_armor%5D=&filterrific%5Btype_like%5D=&filterrific%5Bhouse_like%5D=4&filterrific%5Brarity_like%5D=&filterrific%5Bwith_expansion%5D=1&filterrific%5Bwith_tags%5D=&filterrific%5Bsorted_by%5D=number_asc&commit=Filter+Results




