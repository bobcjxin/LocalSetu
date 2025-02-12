import sqlite3
from pathlib import Path


dir_path = Path(__file__).parent
db_path = dir_path.parent/'LocalSetu.db'
column_list = ['id','url','anti_url','user','date','tag','r18','man','pixiv_id','pixiv_tag','pixiv_tag_t','pixiv_name','pixiv_url','verify','tencent_url']

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(
    '''create table if not exists LocalSetu(
        id integer primary key not null,
        url TEXT(255) not null,
        anti_url TEXT(255) default '',
        user integer(11) default null,
        date text default null,
        tag TEXT(255) default null,
        r18 integer default 0,
        man integer default 0,
        pixiv_id integer(255) default 0,
        pixiv_tag text(255) default '',
        pixiv_tag_t text(255) default '',
        pixiv_name TEXT(255) default '',
        pixiv_url TEXT(255) default '',
        verify integer default 0,
        tencent_url TEXT(255))''')
conn.commit()

def test_conn():
    try:
        conn.ping()
    except:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
def update_db():
    test_conn()
    cursor.execute('''select count(*) from pragma_table_info('LocalSetu')''')
    column_num = cursor.fetchone()[0]
    msg = ''
    for each in column_list[1:column_num]:
        msg += f"{each},"
    msg = msg.strip(',')
    sql = f"""
    DROP table if exists TempOldTable;
    ALTER TABLE LocalSetu RENAME TO TempOldTable;
    create table if not exists LocalSetu(
        id integer primary key not null,
        url TEXT(255) not null,
        anti_url TEXT(255) default '',
        user integer(11) default null,
        date text default null,
        tag TEXT(255) default null,
        r18 integer default 0,
        man integer default 0,
        pixiv_id integer(255) default 0,
        pixiv_tag text(255) default '',
        pixiv_tag_t text(255) default '',
        pixiv_name TEXT(255) default '',
        pixiv_url TEXT(255) default '',
        verify integer default 0,
        tencent_url TEXT(255));
    INSERT INTO LocalSetu ({msg}) SELECT {msg} FROM TempOldTable;
    DROP TABLE TempOldTable;
    """
    cursor.executescript(sql)
    conn.commit()
        

class getImgDao:
    def __init__(self):
        test_conn()
        
    def get_local_image_random(self, is_man):
        """随机图片
        id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify
        """
        sql = 'SELECT * FROM LocalSetu'
        cursor.execute(sql)
        conn.commit()
        print('='*25)
        print(cursor.fetchall())
        print('='*25)

        sql="SELECT id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify FROM LocalSetu where man = ? ORDER BY random() limit 1"
        cursor.execute(sql,(is_man,))
        conn.commit()
        # print(cursor.fetchone())
        return cursor.fetchone()
    
    def get_local_image_user(self, is_man,user):  
        """根据用户查找图片
        id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify
        """
        sql="SELECT id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify from LocalSetu where man = ? AND user = ? ORDER BY random() limit 1"
        cursor.execute(sql,(is_man,str(user)))
        conn.commit()
        return cursor.fetchone()
    
    def get_local_image_ID(self, is_man,id):
        """根据ID查找图片
        id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify
        """
        test_conn()
        sql="SELECT id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify FROM LocalSetu where man = ? AND id = ? ORDER BY random() limit 1"
        cursor.execute(sql,(is_man,id))
        conn.commit()
        return cursor.fetchone()
    
    def get_local_image_tag(self, is_man,tag):
        """根据TAG查找图片
        id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify
        """
        test_conn()
        sql="SELECT id,url,anti_url,user,date,tag,pixiv_tag_t,pixiv_id,pixiv_url,verify FROM LocalSetu where man = ? AND (tag like ? OR pixiv_tag like ? OR pixiv_tag_t like ?) ORDER BY random() limit 1"
        cursor.execute(sql,(is_man,tag,tag,tag))
        conn.commit()
        return cursor.fetchone()
    
    def get_original_image(self, id):
        """查询原图是否存在
        pixiv_url,verify,pixiv_name,pixiv_id,url
        """
        test_conn()
        sql="SELECT pixiv_url,verify,pixiv_name,pixiv_id,url FROM LocalSetu where id = ?"
        cursor.execute(sql,(id,))
        conn.commit()
        return cursor.fetchone()
    
    def update_original_image(self,pixiv_id,pixiv_tag,pixiv_tag_t,r18,pixiv_img_url,pixiv_name,id):
        """更新原图信息"""
        test_conn()
        sql = "update LocalSetu set pixiv_id = ?,pixiv_tag = ?,pixiv_tag_t = ?,r18 = ?,pixiv_url = ?,pixiv_name = ? where id = ?"
        cursor.execute(sql,(pixiv_id,pixiv_tag,pixiv_tag_t,r18,pixiv_img_url,pixiv_name,id))
        conn.commit()
        
class loadImgDao:
    def __init__(self):
        test_conn()
        
    def load_image(self,url,user,tag,is_man,tencent_url):
        """上传消息类型的图片"""
        test_conn()
        sql="INSERT OR IGNORE INTO LocalSetu (id,url,user,date,tag,man,tencent_url) VALUES (NULL,?,?,datetime('now','localtime'),?,?,?)"
        cursor.execute(sql,(url,user,tag,is_man,tencent_url))
        id=cursor.lastrowid
        conn.commit()
        return id
    
    #好像文件类型没啥区别？先用消息的了
    def load_file(self,url,user,tag,is_man):
        """上传文件类型的图片"""
        sql="INSERT OR IGNORE INTO LocalSetu (id,url,user,date,tag,man) VALUES (NULL,?,?,datetime('now'),?,?)"
        cursor.execute(sql,(url,user,tag,is_man))
        id=cursor.lastrowid
        conn.commit()
        return
    
    def check_url(self,url):
        """检查url是否重复"""
        sql="SELECT id FROM LocalSetu where url = ?"
        cursor.execute(sql,(url,))
        conn.commit()
        return cursor.fetchone()
     
        
class deleteDao:
    def __init__(self):
        test_conn()
        
    def get_info(self,id):
        """检查上传用户和url"""
        test_conn()
        sql="select url,user from LocalSetu where id = ?"
        cursor.execute(sql,(id,))
        conn.commit()
        return cursor.fetchall()
    
    def apply_for_delete(self,id):
        """申请删除色图"""
        test_conn()
        sql="update LocalSetu set verify = 2 where id = ?"
        cursor.execute(sql,(id,))
        conn.commit()
        
    def delete_image(self,id):
        """删除色图"""
        test_conn()
        sql="delete from LocalSetu where id = ?"
        cursor.execute(sql,(id,))
        conn.commit()
            
        
class verifyDao:
    def __init__(self):
        test_conn()
        
    def update_verify_stats(self,id:int, data:int):
        """
        更新审核状态
        id: 色图ID
        data: 0:通过, 1:待审核
        """
        try:
            test_conn()
            sql = f"update LocalSetu set verify = {data} where id = ?"
            cursor.execute(sql,(id,))
            conn.commit()
            return data
        except:
            return 1

    def update_verify_info(self,id:int, pixiv_id ,pixiv_tag ,pixiv_tag_t ,r18 ,pixiv_url ):
        """
        更新审核信息
        id: 色图ID
        pixiv_id: P站作品ID
        pixiv_tag：日文TAG
        pixiv_tag_t: 中文TAG
        r18： 是否R18
        pixiv_url： P站大图链接
        """
        try:
            test_conn()
            sql = "update LocalSetu set pixiv_id = ?,pixiv_tag = ?,pixiv_tag_t = ?,r18 = ?,pixiv_url = ? where id = ?"
            cursor.execute(sql,(pixiv_id,pixiv_tag,pixiv_tag_t,r18,pixiv_url,id))
            conn.commit()
            return 0
        except:
            return 1
        
    def get_verify_info(self,verify):
        """获取待审核图信息
        url,user,date,id,man
        """
        test_conn()
        sql="select url,user,date,id,man from LocalSetu where verify = ? ORDER BY random() limit 1"
        cursor.execute(sql,(verify,))
        return cursor.fetchone()
    
    def get_verify_list(self,id):
        """从指定ID开始获取待审核图信息"""
        test_conn()
        sql="SELECT id,url FROM LocalSetu where (pixiv_id = 0 or verify = 1) and id >= ?"
        cursor.execute(sql,(id,))
        return cursor.fetchall()
        

class normalDao:
    def __init__(self):
        test_conn()
        
    def get_all_info(self,id):
        """获取全部信息"""
        test_conn()
        sql="SELECT * FROM LocalSetu where id = ?"
        cursor.execute(sql,(id,))
        return cursor.fetchone()
    
    def get_tecent_url_list(self):
        """获取存在腾讯URL的全部图片"""
        test_conn()
        sql="SELECT id FROM LocalSetu where tencent_url is not NULL"
        cursor.execute(sql)
        return cursor.fetchall()
        
    def get_tecent_url(self,id):
        """检查腾讯url是否存在"""
        test_conn()
        sql="SELECT url,tencent_url FROM LocalSetu where id = ?"
        cursor.execute(sql,(id,))
        return cursor.fetchone()
    
    def update_tag(self,tag,id):
        """更新TAG"""
        test_conn()
        sql="update LocalSetu set tag = ? where id = ?"
        cursor.execute(sql,(tag,id))
        conn.commit()
        
    def get_anti_url(self,id):
        """获取反和谐信息"""
        test_conn()
        sql="SELECT url,anti_url FROM LocalSetu where id =? ORDER BY random() limit 1"
        cursor.execute(sql,(id,))
        conn.commit()
        return cursor.fetchall()
    
    def update_anti_url(self,anti_url,id):
        """更新反和谐url"""
        test_conn()
        sql="update LocalSetu set anti_url = ? where id = ?"#保存反和谐后地址
        cursor.execute(sql,(anti_url,id))
        conn.commit()
        
    def get_image_count(self):
        """获取图库总数"""
        test_conn()
        sql = "select count(*) as sumnumber from LocalSetu"
        cursor.execute(sql)
        conn.commit()
        return cursor.fetchone()
        
    def get_image_upload_rank(self):
        """获取上传前十"""
        test_conn()
        sql = "select user,count(user) as number from LocalSetu GROUP BY user ORDER BY number desc limit 10"
        cursor.execute(sql)
        conn.commit()
        return cursor.fetchall()