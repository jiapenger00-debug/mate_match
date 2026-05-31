// static/demo-data.js
const DEMO_EXAMPLES = [
  {
    id: "art-x-logic", label: "文艺 × 理工", emoji: "🎨", desc: "林小曼 & 张浩然",
    girl: { name: "林小曼", age: 25, hometown: "成都", occupation: "UI 设计师", edu_level: "本科", edu_school: "浙江大学", edu_tags: "985,211,双一流", appearance: "身高163，长发微卷，笑起来很甜", personality: "开朗乐观，有点小文艺，对生活有仪式感。偶尔会有选择困难症，遇到大事会犹豫。", interests: "周末探店拍照、逛展览、手冲咖啡、瑜伽、偶尔画水彩", values: "希望两个人能一起成长，互相欣赏对方的闪光点。不追求大富大贵，但要有品质的生活。家庭观念重。", extra_info: "有一只叫豆豆的橘猫，养了三年", requirements: "有责任心和上进心，能理解她的浪漫和仪式感，最好也喜欢小动物" },
    user: { name: "张浩然", age: 28, hometown: "西安", occupation: "后端开发工程师", edu_level: "硕士", edu_school: "浙江大学", edu_tags: "985,211,双一流", appearance: "身高178，偏瘦，戴黑框眼镜，喜欢穿卫衣", personality: "偏内向但熟了话很多，做事认真靠谱，喜欢提前规划。有时候太理性，不太会表达感情。", interests: "骑行、玩 Switch、周末研究新菜谱、看科幻电影、偶尔打羽毛球", values: "追求技术上的成长，但更看重 work-life balance。希望找一个能理解程序员节奏的伴侣。", extra_info: "养了一只柯基叫肉松，已经两岁了", requirements: "温柔独立，有自己的生活，能尊重彼此的节奏和空间" }
  },
  {
    id: "lively-x-calm", label: "活泼 × 沉稳", emoji: "🔥", desc: "小野 & 老陈",
    girl: { name: "小野", age: 24, hometown: "长沙", occupation: "新媒体运营", edu_level: "本科", edu_school: "北京外国语大学", edu_tags: "211,双一流", appearance: "身高160，短发干练，总是笑嘻嘻的", personality: "社交天花板，朋友遍布全城，走到哪都能交到朋友。话多但不烦人，擅长活跃气氛。偶尔会冲动消费。", interests: "脱口秀、蹦迪、剧本杀、拍抖音、吃遍各种网红店", values: "活在当下，体验生活。觉得人生就应该有趣，不想被条条框框束缚。但也渴望一段稳定的感情。", extra_info: "家里有只布偶猫叫团子，朋友圈全是它的表情包", requirements: "能接受她话多和偶尔的冲动，但能给她安全感，年龄不是问题" },
    user: { name: "老陈", age: 29, hometown: "南京", occupation: "建筑设计师", edu_level: "硕士", edu_school: "东南大学", edu_tags: "985,211,双一流", appearance: "身高182，身材壮实，喜欢穿衬衫", personality: "温和少言，做事有条有理，情绪稳定。不喜欢吵闹，但对亲近的人很有耐心。会默默记住别人说过的话。", interests: "看纪录片、逛博物馆、木工手作、养多肉植物", values: "追求匠人精神，相信慢工出细活。想找一个能互补的另一半，一个闹一个静刚刚好。", extra_info: "阳台种了30多盆多肉，每一盆都有名字", requirements: "开朗阳光，给生活带来色彩，不需要多文靜，真诚就好" }
  },
  {
    id: "elite-x-free", label: "精英 × 自由", emoji: "👔", desc: "Lisa & 阿凯",
    girl: { name: "Lisa", age: 31, hometown: "北京", occupation: "投行 VP", edu_level: "MBA", edu_school: "北京大学", edu_tags: "985,211,双一流", appearance: "身高168，精致妆容，气场强但笑起来很温柔", personality: "职场上是女王，私下其实很会照顾人。目标感极强，习惯把事情做到极致。偶尔会因为太忙忽略生活。", interests: "品酒、高尔夫、看财经新闻、偶尔去海边度假", values: "追求卓越，但意识到人生不只有工作。渴望遇到一个让自己愿意慢下来的人，共同经营有质感的生活。", extra_info: "有一只金毛叫Max，因为太忙都是爸妈在养", requirements: "有品位有见识，懂生活情趣，不介意她忙，但能让她愿意为了他慢下来" },
    user: { name: "阿凯", age: 30, hometown: "大理", occupation: "独立摄影师", edu_level: "本科", edu_school: "中国美术学院", edu_tags: "双一流", appearance: "身高176，扎小辫，手臂有纹身，很有艺术气息", personality: "自由浪漫，不喜欢被规则束缚。感性大于理性，靠直觉做判断。对美有执念，对钱不太计较。真诚但不靠谱。", interests: "旅行摄影、冲浪、弹吉他、研究咖啡豆、写博客", values: "人生是旷野不是轨道。想做自己喜欢的事，遇到喜欢的人。不在乎对方赚多少，更在乎灵魂有没有趣。", extra_info: "在大理有一个小工作室，养了一只流浪猫叫小黑", requirements: "不势利，灵魂有趣，能接受自由职业的不确定性，愿意一起探索世界" }
  },
  {
    id: "dev-x-dev", label: "码农 × 码农", emoji: "💻", desc: "小齐 & 阿飞",
    girl: { name: "小齐", age: 27, hometown: "武汉", occupation: "前端工程师", edu_level: "本科", edu_school: "华中科技大学", edu_tags: "985,211,双一流", appearance: "身高164，素颜，舒服耐看型", personality: "理性+温柔，debug时专注得像换了个人。私下有点宅但很愿意为喜欢的人做饭。对感情认真但不善于主动。", interests: "写博客、逛 GitHub、研究新框架、周末做烘焙、偶尔玩桌游", values: "技术改变世界也要经营好小日子。希望找个同行，互相理解加班和debug的压力，一起写代码一起生活。", extra_info: "GitHub 500+ star，博客月阅读量过万", requirements: "技术好是加分项但不是必须，重要的是有共同的成长心态，愿意一起折腾" },
    user: { name: "阿飞", age: 28, hometown: "杭州", occupation: "全栈工程师", edu_level: "本科", edu_school: "电子科技大学", edu_tags: "985,211,双一流", appearance: "身高175，不修边幅，但写代码时很帅", personality: "典型 nerd，对技术极度热情，生活中有些笨拙。但很真诚，答应的事一定做到。周末会主动学新东西。", interests: "开源贡献、玩树莓派、看科幻、打乒乓球、研究各种效率工具", values: "想做有价值的技术。希望两个人能一起写 side project，互相 review 代码，周末 hackathon。", extra_info: "有一个开源项目 2K star，家里全是各种电子设备", requirements: "不嫌弃 nerdy 的日常，有自己的爱好，互相理解加班和 debug 的压力" }
  }
];
