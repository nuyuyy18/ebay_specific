import typer
import uvicorn
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from ebay import open_ebay, parse, scrape_detail

app = FastAPI()
cli = typer.Typer()

@app.get("/scrape")
def scrape_api(query: str, pages: int = 1):
    driver = open_ebay(query, pages)
    data = parse(driver, pages)
    return JSONResponse(content=data)

@app.get("/detail")
def detail_api(url: str):
    data = scrape_detail(url)
    return JSONResponse(content=data)


@cli.command()
def scrape(query: str, pages: int = 1):
    """Scrape product list from eBay"""
    driver = open_ebay(query, pages)
    data = parse(driver, pages)
    typer.echo(data)

@cli.command()
def detail(url: str):
    """Scrape product detail from eBay"""
    data = scrape_detail(url)
    typer.echo(data)

@cli.command()
def runserver(host: str = "127.0.0.1", port: int = 8000):
    """Run FastAPI server"""
    uvicorn.run("app:app", host=host, port=port, reload=True)

if __name__ == "__main__":

    cli = typer.Typer()

    @cli.command()
    def runserver(host: str = "127.0.0.1", port: int = 8000):
        """Run FastAPI server"""
        uvicorn.run("app:app", host=host, port=port, reload=True)

    cli()
