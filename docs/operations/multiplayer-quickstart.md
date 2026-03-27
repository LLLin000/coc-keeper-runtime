# Multiplayer Quickstart

## Goal

Run a real multiplayer session in one Discord channel with natural player messages instead of requiring `/turn` every time.

## Setup

1. Start the bot locally.
2. Invite the bot to your server.
3. In the target channel, run:
   - `/setup`
   - `/bind_campaign campaign_id:test1`
4. Each player runs:
   - `/join_campaign`

Optional:

- `/import_character provider:dicecloud_snapshot external_id:<id>`
- `/load_adventure adventure_id:starter_crypt`

## How Players Speak

Players normally just type in the channel.

Examples of processed messages:

- `我检查石棺边缘有没有机关。`
- `我对酒馆老板说：昨晚到底发生了什么？`
- `@队友 我先进去，你帮我盯住门口。`

Examples of ignored messages:

- `//等下，我去接个电话`
- `@队友 你今晚几点有空`

## Scene Flow

- `/enter_scene speakers:酒馆老板,守卫,神秘旅人`
- 玩家正常说话
- bot 会以更明确的说话人标签输出多角色台词
- `/end_scene` 返回普通 DM 模式

## Combat Flow

1. `/start_combat combatants:Hero:15:20:15,Goblin:12:7:13`
2. `/show_combat` 查看当前顺序
3. 当前行动者直接发普通消息描述动作
4. 其他玩家若发正式动作，会收到“当前轮到谁”的提示
5. `/next_turn` 推进回合

## Fallback

如果你怀疑自然消息过滤误判，仍然可以使用：

- `/turn content:我推开门。`

这条命令始终作为保底和调试入口保留。
