import asyncio

from dotenv import load_dotenv

from lecturia.chains.tts import create_tts_chain, Talk


load_dotenv()

async def main(args):
    tts = create_tts_chain()
    audio = await tts.ainvoke(
        text=args.text,
        voice_type="senior_male",
    )
    audio.save_mp3("output_audio.mp3")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    args = parser.parse_args()
    asyncio.run(main(args))
