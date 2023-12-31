import asyncio

class ParserPipeline:
    def __init__(self, parser, time_to_sleep, db_processer) -> None:
        self.parser = parser
        self.time_to_sleep = time_to_sleep
        self.db_processer = db_processer

    async def run(self):
        while True:
            data = await self.parser.parse()
            await self.db_processer(data)
            await asyncio.sleep(self.time_to_sleep)


class BalansePipepline(ParserPipeline):
    def __init__(self, parser, time_to_sleep, db_processer) -> None:
        super().__init__(parser, time_to_sleep, db_processer)

class TransactionsPipepline(ParserPipeline):
    def __init__(self, parser, time_to_sleep, db_processer) -> None:
        super().__init__(parser, time_to_sleep, db_processer)

    async def run(self):
        while True:
            block = await self.db_processer.get_last_block(self.parser.address)
            data = await self.parser.parse(start_block=block)
            await self.db_processer(data)
            await asyncio.sleep(self.time_to_sleep)

class App:
    def __init__(self):
        self.pipelines = []

    def add_pipeline(self, pipeline):
        self.pipelines.append(pipeline)

    async def run_all_pipelines(self):
        tasks = [pipeline.run() for pipeline in self.pipelines]
        await asyncio.gather(*tasks)

    async def start(self):
        await self.run_all_pipelines()
    