import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Register a team
        res = await client.post("http://localhost:8000/api/team/register", json={"team_name": "TestTeam"})
        team = res.json()["team"]
        print("Registered team:", team)

        # 2. Create a session
        res = await client.post("http://localhost:8000/api/session/create", json={"session_id": "test_sess", "status": "waiting"})
        print("Created session:", res.json())

        # 3. Add team to session
        res = await client.put(f"http://localhost:8000/api/host/edit_team/{team['team_id']}", json={"session_id": "test_sess"})
        print("Edit team:", res.json())

        # 4. Fetch all teams
        res = await client.get("http://localhost:8000/api/host/teams")
        for t in res.json()["teams"]:
            if t["team_id"] == team["team_id"]:
                print("Team in DB:", t)

if __name__ == "__main__":
    asyncio.run(main())
